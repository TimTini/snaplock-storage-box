"""Compare native rib expressions with SCAD, or audit a real Fusion export.

Default mode uses offline CSG and does not execute Fusion's solver or kernel.
--native DIRECTORY compares native-exported bodies to SCAD with identical inputs.
"""
import argparse
import importlib.util
import json
from pathlib import Path

import manifold3d as manifold
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


model=module('native_rib_model',ROOT/'fusion/SnaplockStorageBox/SnaplockStorageBox.py')
scad=module('rib_scad_audit',ROOT/'tools/audit-scad.py')
native=module('rib_native_audit',ROOT/'tools/audit-fusion.py')


def evaluate(expression,values):
    return eval(expression.replace(' mm','').replace(';',','),{'__builtins__':{},
        'min':min,'max':max,'ceil':np.ceil,'sqrt':np.sqrt},values)


def solid(mesh):
    return manifold.Manifold(manifold.Mesh64(np.asarray(mesh.vertices,dtype=np.float64),
        np.asarray(mesh.faces,dtype=np.uint64)))


def compare(mesh,reference):
    current=mesh.copy()
    translation=reference.bounds[0]-current.bounds[0]
    current.apply_translation(translation)
    a,b=solid(current),solid(reference)
    extra,missing=(a-b).volume(),(b-a).volume()
    return {'translation_mm':translation.tolist(),'volume_mm3':float(current.volume),
            'reference_volume_mm3':float(reference.volume),
            'bounds_error_mm':float(np.abs(current.bounds-reference.bounds).max()),
            'extra_mm3':extra,'missing_mm3':missing,
            'symmetric_difference_percent':float(100*(extra+missing)/reference.volume)}


def polygon_extrude(spec,values):
    points=[[evaluate(x,values),evaluate(y,values)] for x,y in spec['coords']]
    height=evaluate(spec['distance'],values)
    shape=manifold.CrossSection([points],manifold.FillRule.NonZero).extrude(height)
    offset=evaluate(spec.get('offset','0 mm'),values)
    if spec['base']=='xy':
        transform=[[1,0,0,0],[0,1,0,0],[0,0,1,offset]]
    elif spec['base']=='yz':
        transform=[[0,0,1,offset],[1,0,0,0],[0,1,0,0]]
    else:
        transform=[[1,0,0,0],[0,0,1,offset],[0,1,0,0]]
    return shape.transform(np.asarray(transform,dtype=float))


def offline_body(base,p,flags):
    values=dict(p,**model.dimensions(p))
    expected=model.reinforcement_dimensions(p)
    for name,(_,expression) in model.RIB_DERIVED.items():
        values[name]=evaluate(expression,values)
    for axis in ('x','y'):
        assert values['rib_count_'+axis]==expected['count_'+axis]
    result=manifold.Manifold()
    for spec in model.reinforcement_specs(flags):
        seed=polygon_extrude(spec,values)
        if spec['mirror']:
            transform=np.eye(4)[:3]
            other=1 if spec['axis']=='x' else 0
            transform[other,other]=-1
            transform[other,3]=p['width' if other==1 else 'length']
            seed=seed+seed.transform(transform)
        for index in range(int(values['rib_count_'+spec['axis']])):
            transform=np.eye(4)[:3]
            transform[0 if spec['axis']=='x' else 1,3]=index*values['rib_step_'+spec['axis']]
            result=result+seed.transform(transform)
    if any(flags.values()):
        for spec in model.reinforcement_trim_specs():
            result=result-polygon_extrude(spec,values)
    # Native Body already has these exact planar bevels. Keep the independently
    # rendered SCAD shell intact here: its eps hull end-caps differ slightly
    # from Fusion's ideal planar Loft and are outside this rib-only comparison.
    result=solid(base)+result
    mesh=result.to_mesh64()
    current=trimesh.Trimesh(np.asarray(mesh.vert_properties)[:,:3],np.asarray(mesh.tri_verts))
    removed=0
    if not current.is_volume:
        pieces=current.split(only_watertight=False)
        solids=[piece for piece in pieces if piece.is_volume]
        fragments=[piece for piece in pieces if not piece.is_volume]
        # Coplanar intersections can collapse on trimesh's vertex merge. Apply
        # the SCAD export audit's existing zero-width fragment contract only.
        assert solids and all(piece.area<1e-5 and abs(piece.volume)<1e-8
                              for piece in fragments), 'Nontrivial offline CSG fragment'
        removed=sum(len(piece.faces) for piece in fragments)
        current=trimesh.util.concatenate(solids)
    current.metadata['removed_zero_width_faces']=removed
    return current


def definitions(p,flags):
    return [name+'='+str(value) for name,value in p.items()]+[
        name+'='+str(value).lower() for name,value in flags.items()]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'exports/fusion-rib-offline')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    report={'script_sha256':native.sha(native.SCRIPT),'scad_sha256':native.sha(scad.SCAD),
            'mode':'native export' if args.native else 'offline expression CSG; Fusion runtime pending',
            'alignment':'minimum-corner translation only','cases':{}}
    if args.native:
        manifest,meshes=native.load_exports(args.native)
        p=manifest['parameters_mm']
        if set(p)!=set(model.DEFAULTS):
            raise ValueError('Expected complete native parameter manifest')
        model.dimensions(p)
        flags=manifest['reinforcement']
        model.reinforcement_specs(flags)
        report.update(parameters_mm=p,reinforcement=flags)
        for name,mesh in meshes.items():
            part='latch' if name.startswith('Latch') else name.lower()
            reference=scad.build(part,args.output/(name.replace(' ','-')+'-scad.stl'),definitions(p,flags))
            row=compare(mesh,reference)
            row['within_target']=row['bounds_error_mm']<.03 and row['symmetric_difference_percent']<.3
            report['cases'][name]=row
            print(name,json.dumps(row),flush=True)
    else:
        report['configurations_mm']={}
        report['mask_bit_order']=['wall_ribs','wall_floor_ribs','floor_ribs']
        for label,updates in [('original',{}),('printer',dict(length=240,width=220,body_height=100)),
                              ('minimum',dict(length=107.9,width=30.1,body_height=30.2,lid_height=12.5))]:
            p=dict(model.DEFAULTS,**updates)
            report['configurations_mm'][label]=p
            off=dict.fromkeys(model.BUILD_RIBS,False)
            base=scad.build('body',args.output/(label+'-off.stl'),definitions(p,off))
            for mask in range(8):
                flags=dict(zip(('wall_ribs','wall_floor_ribs','floor_ribs'),[bool(mask&(1<<i)) for i in range(3)]))
                reference=scad.build('body',args.output/(label+'-'+str(mask)+'-scad.stl'),definitions(p,flags))
                current=offline_body(base,p,flags)
                assert current.is_volume and len(current.split())==1
                row=compare(current,reference)
                row['removed_zero_width_faces']=current.metadata['removed_zero_width_faces']
                row['symmetric_difference_mm3']=row['extra_mm3']+row['missing_mm3']
                row['within_target']=row['bounds_error_mm']<.005 and abs(row['symmetric_difference_mm3'])<.2
                report['cases'][label+'-'+str(mask)]=row
                print(label,mask,round(row['symmetric_difference_mm3'],6),'mm3',flush=True)
    report['within_target']=all(row['within_target'] for row in report['cases'].values())
    report['status']='passed' if report['within_target'] else 'failed'
    (args.output/'audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if not report['within_target']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
