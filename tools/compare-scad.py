"""Inspectable source/SCAD overlays; run after audit-scad.py."""
from importlib.machinery import SourceFileLoader
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

audit = SourceFileLoader('audit_scad', str(Path(__file__).with_name('audit-scad.py'))).load_module()
out = audit.ROOT / 'outputs/default'
refs = audit.references()
report = json.loads((out / 'audit.json').read_text(encoding='utf-8'))
assert report['scad_sha256'] == hashlib.sha256(audit.SCAD.read_bytes()).hexdigest(), 'Run audit-scad.py to rebuild current SCAD'
assert report['source_sha256'] == audit.HASH, 'Audit source differs'
for name in refs:
    assert report['parts'][name]['export_sha256'] == hashlib.sha256((out / f'{name}.stl').read_bytes()).hexdigest(), f'{name}: export differs from audit'
models = {name: trimesh.load_mesh(out / f'{name}.stl') for name in refs}

fig, axes = plt.subplots(3, 3, figsize=(15, 12))
for row, (name, source) in enumerate(refs.items()):
    cuts = [(0, 18), (0, 21), (0, 26)] if name != 'latch' else [(2, .1), (2, 3), (2, 5.9)]
    for ax, (axis, level) in zip(axes[row], cuts):
        for mesh, color, label in [(source, '#222222', 'STL'), (models[name], '#e05030', 'SCAD')]:
            section = mesh.section(plane_origin=np.eye(3)[axis]*level, plane_normal=np.eye(3)[axis])
            if section:
                for j, curve in enumerate(section.discrete):
                    coordinates = [i for i in range(3) if i != axis]
                    ax.plot(curve[:, coordinates[0]], curve[:, coordinates[1]], color=color,
                            lw=1, label=label if j == 0 else None)
        ax.set_title(f'{name}: {"XYZ"[axis]}={level} mm')
        ax.set_aspect('equal'); ax.grid(alpha=.25); ax.legend()
fig.tight_layout(); fig.savefig(out / 'sections.png', dpi=150); plt.close(fig)

fig = plt.figure(figsize=(15, 8))
for i, (name, source) in enumerate(refs.items()):
    for j, (mesh, title) in enumerate([(source, 'Original STL'), (models[name], 'Editable SCAD')]):
        ax = fig.add_subplot(2, 3, j*3+i+1, projection='3d')
        faces = Poly3DCollection(mesh.triangles, linewidths=0)
        light = .35+.6*np.clip(mesh.face_normals @ np.array([.2, -.5, .8]), 0, 1)
        faces.set_facecolor(light[:, None]*np.array([.25, .65, .85]))
        ax.add_collection3d(faces)
        c = source.bounds.mean(0); r = source.extents.max()*.53
        ax.set(xlim=(c[0]-r,c[0]+r), ylim=(c[1]-r,c[1]+r), zlim=(c[2]-r,c[2]+r))
        ax.set_box_aspect((1,1,1)); ax.view_init(35,-60); ax.set_proj_type('ortho'); ax.set_axis_off()
        ax.set_title(f'{name} — {title}')
fig.tight_layout(); fig.savefig(out / 'comparison.png', dpi=170); plt.close(fig)

subprocess.run([str(audit.OPENSCAD), '--backend', 'Manifold', '--hardwarnings',
                '--render', '--autocenter', '--viewall', '--imgsize', '1500,1050',
                '--projection', 'o', '--camera', '0,0,0,55,0,30,900',
                '-o', str(out / 'preview.png'), str(audit.SCAD)], check=True)
