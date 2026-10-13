"""Compare a current-source Fusion export with original STL and audited SCAD.

Only translations are removed (each part's minimum corner); no scaling, rotation
or ICP is applied. This audits individual shapes, not their assembly positions.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'fusion/SnaplockStorageBox/SnaplockStorageBox.py'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_exports(directory):
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf8'))
    if manifest['script_sha256'] != sha(SCRIPT):
        raise ValueError('Fusion export belongs to another Python source version')
    if manifest['units'] != 'mm' or set(manifest['parts']) != {'Body', 'Lid', 'Latch', 'Latch 2'}:
        raise ValueError('Expected four named parts exported in mm')
    meshes = {}
    for name, row in manifest['parts'].items():
        path = directory / row['file']
        if path.resolve().parent != directory.resolve():
            raise ValueError('Export path escapes selected directory')
        if sha(path) != row['sha256']:
            raise ValueError('STL hash mismatch: ' + name)
        mesh = trimesh.load_mesh(path)
        if not mesh.is_volume or len(mesh.split()) != 1:
            raise ValueError('Expected one closed solid: ' + name)
        meshes[name] = mesh
    return manifest, meshes


def compare(mesh, reference):
    mesh, reference = mesh.copy(), reference.copy()
    translation = (reference.bounds[0] - mesh.bounds[0]).tolist()
    mesh.apply_translation(translation)
    common = trimesh.boolean.intersection([mesh, reference], engine='manifold').volume
    return {'translation_mm': translation, 'volume_mm3': float(mesh.volume),
            'reference_volume_mm3': float(reference.volume),
            'bounds_error_mm': float(np.abs(mesh.bounds - reference.bounds).max()),
            'extra_mm3': float(mesh.volume-common), 'missing_mm3': float(reference.volume-common),
            'symmetric_difference_percent': float(100*(mesh.volume+reference.volume-2*common)/reference.volume)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='Fusion export folder containing manifest.json')
    args = parser.parse_args()
    manifest, meshes = load_exports(args.directory)
    spec = importlib.util.spec_from_file_location('scad_audit', ROOT / 'tools/audit-scad.py')
    scad_audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scad_audit)
    refs = scad_audit.references()  # Validates original STL SHA256.
    scad_report = json.loads((ROOT / 'outputs/default/audit.json').read_text(encoding='utf8'))
    if scad_report['scad_sha256'] != sha(ROOT / 'snaplock-storage-box.scad'):
        raise ValueError('Re-run audit-scad.py: SCAD source changed')
    report = {'script_sha256': manifest['script_sha256'], 'source_sha256': scad_audit.HASH,
              'scad_sha256': scad_report['scad_sha256'], 'alignment': 'minimum-corner translation only',
              'parts': {}}
    passed = True
    for name, mesh in meshes.items():
        key = 'latch' if name.startswith('Latch') else name.lower()
        scad_path = ROOT / 'outputs/default' / (key + '.stl')
        if sha(scad_path) != scad_report['parts'][key]['export_sha256']:
            raise ValueError('SCAD STL hash changed: ' + key)
        row = {'original': compare(mesh, refs[key]),
               'scad': compare(mesh, trimesh.load_mesh(scad_path))}
        row['within_target'] = all(c['bounds_error_mm'] < .03 and
                                   c['symmetric_difference_percent'] < .3 for c in row.values())
        passed = passed and row['within_target']
        report['parts'][name] = row
        print(name, json.dumps(row))
    report['within_target'] = passed
    (args.directory / 'comparison.json').write_text(json.dumps(report, indent=2), encoding='utf8')
    if not passed:
        raise SystemExit('Native geometry differs beyond target: inspect comparison.json')


if __name__ == '__main__':
    main()
