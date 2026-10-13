"""Compare the hybrid spring slot against its pre-change SCAD snapshot."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import time

import numpy as np
import trimesh


def sampled_slot_distance(source, target):
    points = np.vstack((source.vertices, source.triangles_center,
                        trimesh.sample.sample_surface(source, 4000, seed=20261013)[0]))
    selected = ((points[:, 1] >= 6) & (points[:, 1] <= 27) &
                ((points[:, 0] < 5.6) | (points[:, 0] > 22.4)))
    points = np.unique(points[selected], axis=0)
    maximum, worst_point = 0.0, None
    for start in range(0, len(points), 256):
        _, distances, _ = trimesh.proximity.closest_point(target, points[start:start+256])
        index = int(distances.argmax())
        if distances[index] > maximum:
            maximum, worst_point = float(distances[index]), points[start+index].tolist()
    return {'points': len(points), 'max_distance_mm': maximum, 'worst_point_mm': worst_point}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('outputs/slot-hybrid'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('scad_audit', root / 'tools/audit-scad.py')
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    current, baseline = audit.SCAD, args.baseline.resolve()
    assert baseline.is_file() and baseline != current
    reference = audit.references()['latch']
    version = subprocess.run([str(audit.OPENSCAD), '--version'], check=True, capture_output=True, text=True)
    report = {'baseline_sha256': hashlib.sha256(baseline.read_bytes()).hexdigest(),
              'baseline_lf_sha256': hashlib.sha256(baseline.read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
              'scad_sha256': hashlib.sha256(current.read_bytes()).hexdigest(),
              'reference_stl_sha256': audit.HASH, 'resolution_fn': 96,
              'acceptance': {'sampled_slot_distance_mm': .03, 'baseline_symmetric_difference_percent': .03,
                             'baseline_bounds_error_mm': .01, 'reference_symmetric_difference_percent': .1,
                             'reference_bounds_error_mm': .02},
              'openscad_version': (version.stdout+version.stderr).strip(),
              'surface_method': 'bidirectional slot-region vertices, face centres and seeded samples; not Hausdorff',
              'surface_seed': 20261013, 'surface_random_samples': 4000,
              'variants': []}
    args.output.mkdir(parents=True, exist_ok=True)
    for thickness in (5, 6, 6.5):
        meshes, seconds = {}, {}
        for name, path in [('baseline', baseline), ('hybrid', current)]:
            audit.SCAD = path
            start = time.perf_counter()
            meshes[name] = audit.build('latch', args.output / f'{name}-{thickness}.stl',
                                       [f'latch_thickness={thickness}', '$fn=96'])
            seconds[name] = time.perf_counter()-start
            assert meshes[name].is_volume and len(meshes[name].split()) == 1
        old, new = meshes['baseline'], meshes['hybrid']
        common = trimesh.boolean.intersection([old, new], engine='manifold').volume
        row = {'thickness_mm': thickness, 'process_render_load_seconds_single_run': seconds,
               'volume_mm3': float(new.volume), 'faces': len(new.faces),
               'bounds_error_vs_baseline_mm': float(abs(old.bounds-new.bounds).max()),
               'symmetric_difference_vs_baseline_percent': float(100*(old.volume+new.volume-2*common)/old.volume),
               'old_to_new': sampled_slot_distance(old, new),
               'new_to_old': sampled_slot_distance(new, old)}
        if thickness == 6:
            common = trimesh.boolean.intersection([new, reference], engine='manifold').volume
            row['symmetric_difference_vs_stl_percent'] = float(100*(new.volume+reference.volume-2*common)/reference.volume)
            row['bounds_error_vs_stl_mm'] = float(abs(new.bounds-reference.bounds).max())
        report['variants'].append(row)
        (args.output / 'audit.json').write_text(json.dumps(report, indent=2), encoding='utf8')
        print(json.dumps(row), flush=True)
        assert row['bounds_error_vs_baseline_mm'] < .01
        assert abs(row['symmetric_difference_vs_baseline_percent']) < .03
        assert max(row['old_to_new']['max_distance_mm'], row['new_to_old']['max_distance_mm']) < .03
        if thickness == 6:
            assert abs(row['symmetric_difference_vs_stl_percent']) < .1
            assert row['bounds_error_vs_stl_mm'] < .02


if __name__ == '__main__':
    main()
