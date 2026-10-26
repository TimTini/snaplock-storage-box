"""Render SCAD reinforcement variants and validate added material and interfaces.

Run with OPENSCAD set to the installed executable. Outputs stay in exports/.
An optional --baseline-scad snapshot verifies the unchanged default geometry.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('scad_audit',ROOT/'tools/audit-scad.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def volume(mesh):
    return float(mesh.volume) if len(mesh.faces) else 0.0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-scad',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'exports/reinforcement')
    args = parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    report = {'scad_sha256':hashlib.sha256(builder.SCAD.read_bytes()).hexdigest(),
              'scope':'SCAD geometry; physical load validation follows printed samples',
              'cases':{}}
    large = ['length=350','width=200','body_height=100']
    small = ['length=107.9','width=30.1','body_height=30.2','lid_height=11.7']
    off = ['floor_ribs=false','wall_ribs=false','wall_floor_ribs=false']
    on = ['floor_ribs=true','wall_ribs=true','wall_floor_ribs=true']
    cache = {}

    def render(name,definitions,part='body'):
        path = args.output/(name+'.stl')
        mesh = builder.build(part,path,definitions)
        count = len(mesh.split())
        assert mesh.is_volume and count == (4 if part == 'layout' else 1), name+': invalid solids'
        cache[name] = mesh
        report['cases'][name] = {'part':part,'definitions':definitions,
            'bounds_mm':mesh.bounds.tolist(),'volume_mm3':float(mesh.volume),
            'watertight':mesh.is_watertight,'components':count,
            'stl_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        print(name,round(mesh.volume,3),'mm3',count,'solid(s)',flush=True)
        return mesh

    def same(a,b):
        missing = volume(trimesh.boolean.difference([a,b],engine='manifold'))
        extra = volume(trimesh.boolean.difference([b,a],engine='manifold'))
        assert abs(missing)+abs(extra) < .1, 'Expected equal geometry'

    def added(name,base,height,length,width,clearance=5):
        current = cache[name]
        assert np.allclose(current.bounds,base.bounds,atol=.005), name+': outer envelope changed'
        missing = volume(trimesh.boolean.difference([base,current],engine='manifold'))
        addition = trimesh.boolean.difference([current,base],engine='manifold')
        assert abs(missing) < .1, name+': original material removed'
        assert addition.volume > 1, name+': reinforcement added no material'
        # STL float32 can leave thin disconnected boundary slivers after boolean.
        # Bound both individual volume/area and aggregate volume before excluding
        # these numeric remnants from added-region bounds, retaining every rib.
        pieces = addition.split(only_watertight=False)
        remnants = [p for p in pieces if abs(p.volume)<.01 and abs(p.volume)/max(p.area,1e-12)<1e-5]
        remnant_volume = sum(abs(p.volume) for p in remnants)
        assert remnant_volume < .05, name+': excessive boolean numeric remnants'
        solids = [p for p in pieces if not (abs(p.volume)<.01 and abs(p.volume)/max(p.area,1e-12)<1e-5)]
        assert solids, name+': no substantial added ribs'
        addition = trimesh.util.concatenate(solids)
        assert addition.bounds[0,0] >= 3-.02 and addition.bounds[1,0] <= length-3+.02
        assert addition.bounds[0,1] >= 3-.02 and addition.bounds[1,1] <= width-3+.02
        assert addition.bounds[1,2] <= height-clearance+.02, name+': top clearance ignored'
        report['cases'][name].update(added_volume_mm3=float(addition.volume),
            removed_volume_mm3=float(missing),added_bounds_mm=addition.bounds.tolist(),
            boolean_remnant_volume_mm3=float(remnant_volume))
        return addition

    original = render('original_off',off)
    same(original,render('original_default',[]))
    large_off = render('large_off',large+off)
    for name,floor,wall,gusset in [('large_floor',True,False,False),
                                  ('large_wall',False,True,False),
                                  ('large_wall_floor',False,False,True),
                                  ('large_floor_wall',True,True,False),
                                  ('large_floor_gusset',True,False,True),
                                  ('large_wall_gusset',False,True,True),
                                  ('large_all',True,True,True)]:
        modes = ['floor_ribs='+str(floor).lower(),'wall_ribs='+str(wall).lower(),
                 'wall_floor_ribs='+str(gusset).lower()]
        render(name,large+modes)
        added(name,large_off,100,350,200)
    render('large_dense',large+on+['rib_spacing=32','rib_thickness=3','floor_rib_height=6'])
    added('large_dense',large_off,100,350,200)
    small_off = render('minimum_off',small+off)
    same(small_off,render('minimum_default',small))
    render('minimum_all',small+on)
    added('minimum_all',small_off,30.2,107.9,30.1)
    render('original_all',on)
    added('original_all',original,52,237.85,123.15)
    for part in ('lid','latch'):
        same(render(part+'_off',large+off,part),render(part+'_on',large+on,part))
    render('large_layout',large+on,'layout')

    printer = ['length=240','width=220','body_height=100']
    printer_off = render('printer_off',printer+off)
    render('printer_all',printer+on+['wall_rib_top_clearance=20',
        'wall_rib_depth=3','wall_rib_foot=12'])
    added('printer_all',printer_off,100,240,220,20)
    for name,part in [('printer_all','body'),('printer_lid','lid'),('printer_latch','latch')]:
        mesh = cache[name] if name in cache else render(name,printer+on,part)
        assert np.all(mesh.extents <= [250,250,250]), name+': exceeds 250 mm usable print volume'
    report['usable_print_volume_mm'] = [250,250,250]

    enhanced = printer+on+['wall_rib_top_clearance=5','wall_rib_depth=5','wall_rib_foot=20']
    render('printer_enhanced_wall',printer+['wall_ribs=true','wall_floor_ribs=false',
        'floor_ribs=false','wall_rib_top_clearance=5','wall_rib_depth=5'])
    upright = added('printer_enhanced_wall',printer_off,100,240,220)
    assert abs(upright.bounds[1,2]-95) < .02, 'Expected uprights to follow top clearance'
    render('printer_enhanced',enhanced)
    ribs = added('printer_enhanced',printer_off,100,240,220)
    render('minimum_enhanced',small+on+['wall_rib_top_clearance=5',
        'wall_rib_depth=5','wall_rib_foot=20'])
    added('minimum_enhanced',small_off,30.2,107.9,30.1)
    assert abs(volume(trimesh.boolean.difference([cache['printer_all'],cache['printer_enhanced']],
        engine='manifold'))) < .1, 'Enhanced construction removed baseline material'
    lid = cache['printer_lid'].copy()
    closed_transform = np.diag([1.,-1.,-1.,1.])
    closed_transform[:3,3] = [0,220,115]
    lid.apply_transform(closed_transform)
    report['rib_lid_clearance'] = {'placement':'rotate X 180 degrees; translate (0,width,body_height+lid_height)',
        'global_z_gap_mm':float(lid.bounds[0,2]-ribs.bounds[1,2]),'poses':[]}
    assert report['rib_lid_clearance']['global_z_gap_mm'] > .49
    for angle in (0,15,45,90,110):
        moving = lid.copy()
        moving.apply_transform(trimesh.transformations.rotation_matrix(np.deg2rad(angle),
            [1,0,0],point=[0,-4.75,100]))
        overlap = volume(trimesh.boolean.intersection([ribs,moving],engine='manifold'))
        assert abs(overlap) < .01, 'Added ribs collide with lid at '+str(angle)+' degrees'
        report['rib_lid_clearance']['poses'].append({'angle_degrees':angle,'overlap_mm3':overlap})

    if args.baseline_scad:
        baseline = args.baseline_scad.resolve()
        report['baseline_scad_sha256'] = hashlib.sha256(baseline.read_bytes()).hexdigest()
        path = args.output/'baseline_body.stl'
        baseline_mesh = builder.build('body',path,source=baseline)
        same(original,baseline_mesh)
        report['default_matches_baseline'] = True
    report['status'] = 'passed'
    (args.output/'audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
