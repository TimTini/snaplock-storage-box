"""Render and measure closed assemblies across sizes; retain source-bound failures.

The latch clearance classification is separate from measured shell/hinge contact
and from physical fit, deformation, motion clearance and print tolerances.
"""
import argparse
from collections import Counter
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('matrix_latch_fit',ROOT/'tools/audit-latch-fit.py')
fit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(fit)


def cases():
    result=[]
    def add(name,L,W,H,h=15,**extra):
        result.append({'name':name,'parameters':dict(length=L,width=W,body_height=H,lid_height=h,**extra)})
    for L in (107.9,150,200,240):
        for W in (30.1,60,120,220):
            for H in (30.2,50,100):
                add(f'grid-{L}-{W}-{H}',L,W,H)
    add('image-240-120-75',240,120,75)
    add('original-dimensions',237.85,123.15,52)
    for label,L,W,H in [('minimum',107.9,30.1,30.2),('image',240,120,50)]:
        for h in (11.7,12.5,14,16,20):
            add(f'lid-probe-{label}-{h}',L,W,H,h)
    add('image-240-120-25-defaults',240,120,25)
    result[-1]['expected_rejection']='body_height'
    add('image-240-120-25-reduced-bevel',240,120,25,
        bottom_bevel=3,body_inner_bevel=1.5,floor_rib_height=2)
    for L,W,H in [(150,60,50),(240,120,75),(240,220,100)]:
        add(f'reinforced-{L}-{W}-{H}',L,W,H,wall_ribs=True,wall_floor_ribs=True,floor_ribs=True)
    for L in (107.9,250):
        for W in (30.1,232.7):
            for H in (30.2,245.7):
                add(f'boundary-{L}-{W}-{H}',L,W,H)
    add('nominal-250-cube',250,250,250)
    for label,L,W,H in [('minimum',107.9,30.1,30.2),('image',240,120,50)]:
        for h in (25,50,100,233.1,245.5):
            add(f'lid-probe-{label}-{h}',L,W,H,h)
    for label,L,W,H in [('minimum',107.9,30.1,30.2),('middle',180,120,75),('maximum',250,232.7,245.7)]:
        for mask in range(8):
            add(f'ribs-{label}-{mask}',L,W,H,**dict(zip(('wall_ribs','wall_floor_ribs','floor_ribs'),
                [bool(mask&(1<<i)) for i in range(3)])))
    for name,p,bound in [('below-length',dict(length=107.8,width=60,body_height=50),'length'),
                         ('below-width',dict(length=150,width=30,body_height=50),'width'),
                         ('below-body-height',dict(length=150,width=60,body_height=30.1),'body_height'),
                         ('below-lid-height',dict(length=150,width=60,body_height=50,lid_height=11.6),'lid_height')]:
        result.append({'name':name,'parameters':dict(lid_height=15,**p) if 'lid_height' not in p else p,
                       'expected_rejection':bound})
    return result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(part,out,p):
    definitions=[k+'='+str(v).lower() if isinstance(v,bool) else k+'='+str(v) for k,v in p.items()]
    mesh=fit.audit.build(part,out,definitions)
    assert mesh.is_volume and len(mesh.split())==1, 'Expected one closed solid: '+str(out)
    return mesh


def assembly_artifacts(output,report):
    rows=[row for row in report['cases'] if row['status']!='rejected_source_bounds']
    choices=[[row['name']]+[row['parameters'][k] for k in ('length','width','body_height','lid_height')]+[row['latch_file']] for row in rows]
    default=next(i for i,row in enumerate(rows) if row['name']=='grid-240-120-50')
    viewer=f'''// Rigid assembly diagnostic; case index selects the measured meshes.
case_index={default}; // [0:{len(rows)-1}]
show_latch_collision=true;
show_shell_contact=true;
opacity=0.6;
cases={json.dumps(choices)};
c=cases[case_index]; name=c[0]; L=c[1]; W=c[2]; H=c[3]; h=c[4];
echo(name=name, dimensions=[L,W,H], lid_height=h);
module body() {{ import(str(name,"/body.stl")); }}
module lid() {{ translate([0,W,H+h]) rotate([180,0,0]) import(str(name,"/lid.stl")); }}
module latch(x) {{ multmatrix([[1,0,0,x-14],[0,0,1,W],[0,-1,0,H+h-3],[0,0,0,1]]) import(c[5]); }}
color("lightblue",opacity) body();
color("lightgreen",opacity) lid();
for(x=[32.9,L-32.9]) {{
    color("orange") latch(x);
    if(show_latch_collision) color("red") intersection() {{ body(); latch(x); }}
}}
if(show_shell_contact) color("magenta") intersection() {{ body(); lid(); }}
'''
    (output/'assembly.scad').write_text(viewer,encoding='utf-8')
    fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    names=['image-240-120-25-reduced-bevel','grid-240-120-50','image-240-120-75','grid-240-120-100']
    for i,name in enumerate(names):
        row=next(row for row in rows if row['name']==name);p=row['parameters']
        L,W,H,h=(p[k] for k in ('length','width','body_height','lid_height'))
        image=output/name/'assembly-preview.png'
        index=next(j for j,item in enumerate(rows) if item['name']==name)
        result=subprocess.run([str(fit.audit.OPENSCAD),'--imgsize=800,600','--autocenter','--viewall',
            '--camera=0,0,0,65,0,215,500','--render','-D',f'case_index={index}',
            '-D','opacity=1','-D','show_shell_contact=false','-o',str(image),str(output/'assembly.scad')],
            capture_output=True,text=True)
        image.with_suffix('.log').write_text(result.stdout+result.stderr,encoding='utf-8')
        assert result.returncode==0 and image.is_file(),result.stderr
        ax=axes.flat[i];ax.imshow(plt.imread(image));ax.axis('off')
        ax.set_title(f'240 x 120 x {H:g}; lid 15 mm'+('\nReduced bevel control' if H==25 else ''))
    fig.savefig(output/'image-sizes-assemblies.png',dpi=130);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'exports/latch-fit-matrix')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    report={'scope':'closed rigid STL assembly; latch clearance separate from shell/hinge contact and physical fit',
            'scad_sha256':sha(fit.audit.SCAD),'audit_script_sha256':sha(Path(__file__)),
            'assembly_helper_sha256':sha(ROOT/'tools/audit-latch-fit.py'),
            'thresholds':{'each_latch_body_overlap_mm3':.01,'each_latch_lid_overlap_mm3':.01,
                          'latch_latch_overlap_mm3':.01,'body_lid_overlap_mm3':.01},
            'build_volume_mm':[250,250,250],'envelope_numeric_tolerance_mm':.001,'cases':[]}
    latches={}
    for case in cases():
        p=case['parameters']; name=case['name']; directory=args.output/name
        directory.mkdir(exist_ok=True)
        row=dict(case)
        if 'expected_rejection' in case:
            try:
                render('body',directory/'body.stl',p)
            except AssertionError as error:
                detail=str(error)
                assert 'Assertion' in detail and case['expected_rejection'] in detail, detail
                row.update(status='rejected_source_bounds',diagnostic=detail.splitlines()[0])
            else:
                raise AssertionError('Expected source bound rejection: '+name)
        else:
            body=render('body',directory/'body.stl',p)
            lid=render('lid',directory/'lid.stl',p)
            L,W,H,h=(p[k] for k in ('length','width','body_height','lid_height'))
            if h not in latches:
                filename='latch.stl' if h==15 else f'latch-lid-{h}.stl'
                latches[h]=(render('latch',args.output/filename,dict(lid_height=h)),filename)
            latch,latch_file=latches[h]
            top=fit.closed_lid(lid,W,H,h)
            catches=[fit.installed_latch(latch,x,W,H,h) for x in (32.9,L-32.9)]
            b,t=fit.solid(body),fit.solid(top)
            c=[fit.solid(mesh) for mesh in catches]
            body_contact=[max(0.,(b^q).volume()) for q in c]
            lid_contact=[max(0.,(t^q).volume()) for q in c]
            pair_contact=max(0.,(c[0]^c[1]).volume())
            interface=b^t
            shell_contact=max(0.,interface.volume())
            rear_region=fit.manifold.Manifold.cube([L+20,20,H+h+30]).translate([-10,-20,-10])
            rear_contact=max(0.,(interface^rear_region).volume())
            clear=max(body_contact)<.01 and max(lid_contact)<.01 and pair_contact<.01
            row.update(status='closed_clear' if clear and shell_contact<.01 else 'assembly_interference',
                       latch_file=latch_file,latch_sha256=sha(args.output/latch_file),
                       body_extents_mm=body.extents.tolist(),lid_extents_mm=lid.extents.tolist(),
                       stl_sha256={part:sha(directory/(part+'.stl')) for part in ('body','lid')},
                       removed_zero_width_faces={part:mesh.metadata['removed_zero_width_faces']
                           for part,mesh in [('body',body),('lid',lid)]},
                       latch_body_overlap_mm3=body_contact,latch_lid_overlap_mm3=lid_contact,
                       latch_latch_overlap_mm3=pair_contact,body_lid_overlap_mm3=shell_contact,
                       rear_contact_y_negative_mm3=rear_contact,
                       other_shell_contact_mm3=max(0.,shell_contact-rear_contact),
                       latch_socket_world_z_mm=H+h-6,reference_socket_z_delta_mm=h-15,
                       print_envelope_mm={name:mesh.extents.tolist() for name,mesh in [('body',body),('lid',lid),('latch',latch)]},
                       within_print_envelope=all(max(mesh.extents)<=250.001 for mesh in (body,lid,latch)))
            if name in {'lid-probe-minimum-11.7','original-dimensions','ribs-maximum-7',
                        'ribs-minimum-7','lid-probe-image-20','boundary-250-232.7-245.7'}:
                samples=[]
                for angle in (0,.25,1,5,15,45,90,110):
                    opened=top.copy()
                    opened.apply_transform(fit.trimesh.transformations.rotation_matrix(
                        math.radians(angle),[1,0,0],[0,-4.75,H]))
                    samples.append({'angle_deg':angle,'body_lid_overlap_mm3':max(0.,(b^fit.solid(opened)).volume())})
                row['opening_samples_latches_removed']=samples
                row['sampled_opening_clear']=max(sample['body_lid_overlap_mm3'] for sample in samples)<.01
        report['cases'].append(row)
        print(len(report['cases']),name,row['status'],
              round(max(row.get('latch_body_overlap_mm3',[0])),6),flush=True)
        (args.output/'audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    report['counts']=dict(Counter(row['status'] for row in report['cases']))
    report['baseline_lid15_counts']=dict(Counter(row['status'] for row in report['cases']
        if row['parameters']['lid_height']==15))
    report['print_envelope_counts']=dict(Counter('within_250' if row['within_print_envelope'] else 'exceeds_250'
        for row in report['cases'] if 'within_print_envelope' in row))
    (args.output/'audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    with (args.output/'summary.csv').open('w',newline='',encoding='utf-8') as stream:
        fields=['name','length','width','body_height','lid_height','status','max_latch_body_mm3',
                'max_latch_lid_mm3','body_lid_mm3','rear_contact_mm3','other_contact_mm3','within_print_envelope']
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for row in report['cases']:
            writer.writerow(dict(name=row['name'],**{k:row['parameters'][k] for k in fields[1:5]},
                status=row['status'],max_latch_body_mm3=max(row.get('latch_body_overlap_mm3',[0])),
                max_latch_lid_mm3=max(row.get('latch_lid_overlap_mm3',[0])),
                body_lid_mm3=row.get('body_lid_overlap_mm3'),rear_contact_mm3=row.get('rear_contact_y_negative_mm3'),
                other_contact_mm3=row.get('other_shell_contact_mm3'),within_print_envelope=row.get('within_print_envelope')))
    fig,axes=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
    for label in ('minimum','image'):
        rows=sorted([row for row in report['cases'] if row['name'].startswith('lid-probe-'+label)],
                    key=lambda row:row['parameters']['lid_height'])
        ref=next(row for row in report['cases'] if row['name']==('grid-107.9-30.1-30.2' if label=='minimum' else 'grid-240-120-50'))
        rows=sorted(rows+[ref],key=lambda row:row['parameters']['lid_height'])
        axes[0].plot([row['parameters']['lid_height'] for row in rows],
                     [max(row['latch_body_overlap_mm3']) for row in rows],'o-',label=label)
    axes[0].set(xlabel='Lid height (mm)',ylabel='Latch / Body overlap (mm3)',title='Fixed latch versus lid height')
    axes[0].grid(alpha=.2);axes[0].legend()
    rows=[row for row in report['cases'] if row['status']!='rejected_source_bounds' and row['parameters']['lid_height']==15]
    axes[1].scatter([row['parameters']['body_height'] for row in rows],
                    [max(row['latch_body_overlap_mm3']) for row in rows],label='Each tested size')
    axes[1].axhline(.01,color='red',ls=':',label='Clearance audit threshold')
    axes[1].set(xlabel='Body height (mm)',ylabel='Latch / Body overlap (mm3)',title='15 mm lid across body sizes')
    axes[1].grid(alpha=.2);axes[1].legend()
    fig.savefig(args.output/'summary.png',dpi=160);plt.close(fig)
    assembly_artifacts(args.output,report)
    print(json.dumps(report['counts']))
    assert all(row['status'] in {'closed_clear','rejected_source_bounds'} for row in report['cases'])
    assert all(row.get('sampled_opening_clear',True) for row in report['cases'])


if __name__=='__main__':
    main()
