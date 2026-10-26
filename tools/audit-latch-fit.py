"""Rigid assembly diagnostic for the current minimum and a 15 mm lid control.

Each lid height uses its matching parametric latch from current SCAD.
This measures rigid interference, not deformation, snap force or printer accuracy.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import manifold3d as manifold
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('latch_fit_scad',ROOT/'tools/audit-scad.py')
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def solid(mesh):
    return manifold.Manifold(manifold.Mesh64(np.asarray(mesh.vertices,dtype=np.float64),
        np.asarray(mesh.faces,dtype=np.uint64)))


def closed_lid(mesh,width,height,lid_height):
    # Match the binary STL's planar mating datums. Exact decimal translation
    # against float32 vertices creates artificial skins for tall lids.
    width,height,lid_height=(float(np.float32(v)) for v in (width,height,lid_height))
    result=mesh.copy()
    result.apply_transform([[1,0,0,0],[0,-1,0,width],[0,0,-1,height+lid_height],[0,0,0,1]])
    return result


def installed_latch(mesh,anchor,width,height,lid_height):
    width,height,lid_height=(float(np.float32(v)) for v in (width,height,lid_height))
    result=mesh.copy()
    # Rx(-90): latch X -> model X, latch Y -> -Z, thickness Z -> +Y.
    # Align the ball pair midpoint (14,3,t/2) with (anchor,width+3,H+h-6).
    # Source ball pitch is 20.5 mm vs socket pitch 21 mm: +/-0.25 mm X offset.
    t=mesh.extents[2]
    result.apply_transform([[1,0,0,anchor-14],[0,0,1,width+3-t/2],
                            [0,-1,0,height+lid_height-3],[0,0,0,1]])
    return result


def draw_section(ax,mesh,x,color,label):
    section=mesh.section([1,0,0],[x,0,0])
    if section is not None:
        for i,loop in enumerate(section.discrete):
            ax.plot(loop[:,1],loop[:,2],color=color,lw=1.2,label=label if i==0 else None)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'exports/latch-fit-minimum')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    preset=ROOT/'samples/minimum'
    params=json.loads((preset/'parameters.json').read_text())['parameterSets']['print-test-minimum']
    p={name:float(value) for name,value in params.items()}
    L,W,H,h=(p[name] for name in ('length','width','body_height','lid_height'))
    body,lid,latch=(trimesh.load_mesh(preset/(name+'.stl')) for name in ('body','lid','latch'))
    for mesh in (body,lid,latch):
        assert mesh.is_volume and len(mesh.split())==1
    control_path=args.output/'lid-height15.stl'
    control=audit.build('lid',control_path,[name+'='+str(value) for name,value in dict(p,lid_height=15).items()])
    control_latch_path=args.output/'latch-height15.stl'
    control_latch=audit.build('latch',control_latch_path,[name+'='+str(value) for name,value in dict(p,lid_height=15).items()])
    source_latch=audit.references()['latch']
    report={'scope':'rigid STL assembly; physical deformation and snap force require print testing',
            'audit_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scad_sha256':hashlib.sha256(audit.SCAD.read_bytes()).hexdigest(),
            'parameters_mm':p,'input_part_hashes':{name:hashlib.sha256((preset/(name+'.stl')).read_bytes()).hexdigest()
                for name in ('body','lid','latch')},
            'latch_extents_mm':latch.extents.tolist(),'original_latch_extents_mm':source_latch.extents.tolist(),
            'pivot_lowering_mm':15-h,
            'ball_pair_pitch_mm':20.5,'socket_pair_pitch_mm':21,
            'per_ball_inward_x_offset_mm':.25,'poses':{}}
    report['control_lid_sha256']=hashlib.sha256(control_path.read_bytes()).hexdigest()
    fig,axes=plt.subplots(1,2,figsize=(11,6),constrained_layout=True)
    for ax,label,top,lh,matching_latch in zip(axes,('minimum','control-height15'),(lid,control),(h,15),(latch,control_latch)):
        top=closed_lid(top,W,H,lh)
        catches=[installed_latch(matching_latch,anchor,W,H,lh) for anchor in (32.9,L-32.9)]
        overlaps=[(solid(body)^solid(c)).volume() for c in catches]
        pivot_z=H+lh-6
        report['poses'][label]={'lid_height_mm':lh,'lid_socket_world_z_mm':pivot_z,
            'catch_core_world_z_interval_mm':[H-10.0724,H-6.0724],
            'body_pocket_world_z_interval_mm':[H-11.5,H-5],
            'latch_body_overlap_mm3':overlaps,
            'latch_lid_overlap_mm3':[(solid(top)^solid(c)).volume() for c in catches],
            'body_lid_overlap_mm3':(solid(body)^solid(top)).volume()}
        # Separate part solids intentionally overlap in the failed assembly.
        trimesh.util.concatenate([body,top]+catches).export(args.output/(label+'-assembly.stl'))
        for mesh,color,name in [(body,'#1976d2','Body'),(top,'#24812e','Lid'),(catches[0],'#e67e22','Latch')]:
            draw_section(ax,mesh,19.8,color,name)
        intersection=solid(body)^solid(catches[0])
        if intersection.num_tri()>0:
            raw=intersection.to_mesh64()
            overlap=trimesh.Trimesh(np.asarray(raw.vert_properties)[:,:3],np.asarray(raw.tri_verts))
            draw_section(ax,overlap,19.8,'#d81b60','Interference')
        ax.axhline(H,color='#777',ls=':',lw=.8,label='Body rim')
        ax.set(xlim=(W-2,W+11),ylim=(H-16,H+14),aspect='equal',xlabel='Y (mm)',ylabel='Z (mm)',
               title=f'{label}: lid {lh:g} mm\nLatch / Body overlap {overlaps[0]:.4f} mm3')
        ax.grid(alpha=.2)
        ax.legend(loc='upper left',fontsize=8)
    fig.suptitle('Rigid assembly section through the latch tooth (X = 19.8 mm)')
    fig.savefig(args.output/'sections.png',dpi=160)
    plt.close(fig)
    for row in report['poses'].values():
        assert max(row['latch_body_overlap_mm3']+row['latch_lid_overlap_mm3']+[row['body_lid_overlap_mm3']])<.01
    (args.output/'audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    # Editable visual assembly references the exact STL files measured above.
    paths=[(preset/'body.stl').resolve(),(preset/'lid.stl').resolve(),control_path.resolve(),(preset/'latch.stl').resolve(),control_latch_path.resolve()]
    imports=[json.dumps(path.as_posix()) for path in paths]
    viewer=f'''// Rigid diagnostic assembly. Select the two lid heights for comparison.
control_height15 = false;
show_interference = true;
L={L}; W={W}; H={H}; h=control_height15?15:{h};
module body() {{ import({imports[0]}); }}
module lid() {{ translate([0,W,H+h]) rotate([180,0,0])
    if(control_height15) import({imports[2]}); else import({imports[1]}); }}
module latch(x) {{ multmatrix([[1,0,0,x-14],[0,0,1,W],[0,-1,0,H+h-3],[0,0,0,1]])
    if(control_height15) import({imports[4]}); else import({imports[3]}); }}
color("lightblue",0.5) body();
color("lightgreen",0.5) lid();
for(x=[32.9,L-32.9]) {{
    color("orange") latch(x);
    if(show_interference) color("red") intersection() {{ body(); latch(x); }}
}}
'''
    (args.output/'assembly.scad').write_text(viewer,encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
