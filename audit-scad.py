"""Build and compare editable SCAD with the original STL (millimetres)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent
SCAD = ROOT / 'snaplock-storage-box.scad'
OPENSCAD = os.environ.get('OPENSCAD', 'openscad')
SOURCE = ROOT / 'reference' / 'Snaplock_Storage_Boxes_240x120(2).stl'
HASH = '73faaa2d438b02038b9f84002202435973a09f92ec2a48315577e0e00baea167'


def references():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == HASH, 'Source hash changed'
    parts = sorted(trimesh.load_mesh(SOURCE).split(only_watertight=False),
                   key=lambda mesh: len(mesh.faces), reverse=True)
    latch, lid, body = (parts[i].copy() for i in (0, 2, 3))
    latch.vertices -= latch.bounds[0]
    lid.vertices -= [9.07501220703125, 65.8, 0]
    body.vertices = body.vertices[:, [1, 0, 2]] - [1.2428739070892334, 377.83758544921875, 0]
    body.invert()  # Swapping X/Y reverses handedness.
    return dict(body=body, lid=lid, latch=latch)


def build(part, out, definitions=()):
    command = [str(OPENSCAD), '--backend', 'Manifold', '--hardwarnings', '--export-format', 'binstl',
               '-D', f'part="{part}"', '-o', str(out)]
    for definition in definitions:
        command += ['-D', definition]
    result = subprocess.run(command + [str(SCAD)], capture_output=True, text=True)
    (out.with_suffix('.log')).write_text(result.stdout + result.stderr, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    mesh = trimesh.load_mesh(out)
    # Binary STL float32 can collapse coincident intersection triangles to zero
    # width. Remove only these faces; require a closed solid after this step.
    removed = 0
    if not mesh.is_volume:
        pieces = mesh.split(only_watertight=False)
        solids = [piece for piece in pieces if piece.is_volume]
        fragments = [piece for piece in pieces if not piece.is_volume]
        # Preserve closed solids, including their shared boundary triangulation.
        # Discard only disconnected fragments below area/volume tolerances.
        assert solids and all(piece.area < 1e-5 and abs(piece.volume) < 1e-8
                              for piece in fragments), 'Nontrivial fragment: inspect geometry'
        removed = sum(len(piece.faces) for piece in fragments)
        mesh = trimesh.util.concatenate(solids)
        assert mesh.is_volume, 'Export cleanup exposed an open mesh'
        mesh.export(out)
    mesh.metadata['removed_zero_width_faces'] = removed
    return mesh


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', action='store_true')
    args = parser.parse_args()
    out = ROOT / 'exports' / ('variant' if args.variant else 'default')
    out.mkdir(parents=True, exist_ok=True)
    refs = references()
    report = {'source_sha256': HASH, 'scad_sha256': hashlib.sha256(SCAD.read_bytes()).hexdigest(), 'parts': {}}
    for name, reference in refs.items():
        mesh = build(name, out / f'{name}.stl',
                     ['length=280', 'width=155', 'body_height=70'] if args.variant else [])
        assert mesh.is_volume and len(mesh.split()) == 1, f'{name}: invalid solid'
        row = {'bounds': mesh.bounds.tolist(), 'volume_mm3': mesh.volume,
               'watertight': mesh.is_watertight, 'components': len(mesh.split()),
               'removed_zero_width_faces': mesh.metadata['removed_zero_width_faces'],
               'export_sha256': hashlib.sha256((out / f'{name}.stl').read_bytes()).hexdigest()}
        if not args.variant:
            common = trimesh.boolean.intersection([mesh, reference], engine='manifold').volume
            row.update(reference_volume_mm3=reference.volume,
                       bounds_error_mm=float(np.abs(mesh.bounds-reference.bounds).max()),
                       extra_mm3=float(mesh.volume-common), missing_mm3=float(reference.volume-common),
                       symmetric_difference_percent=float(100*(mesh.volume+reference.volume-2*common)/reference.volume))
            assert row['bounds_error_mm'] < .02, f'{name}: source bounds mismatch'
            limit = .1 if name == 'latch' else .2
            assert row['symmetric_difference_percent'] < limit, f'{name}: geometry difference exceeds {limit}%'
        else:
            expected = {'body': [280, 172, 74.25], 'lid': [280, 172.25, 19.5],
                        'latch': [28, 31.835144, 6]}[name]
            assert np.allclose(mesh.extents, expected, atol=.02), f'{name}: variant dimensions ignored'
        report['parts'][name] = row
        print(name, json.dumps(row))
    layout = build('layout', out / 'layout.stl',
                   ['length=280', 'width=155', 'body_height=70'] if args.variant else [])
    assert layout.is_volume and len(layout.split()) == 4, 'Layout must contain four closed solids'
    report['layout_components'] = len(layout.split())
    (out / 'audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
