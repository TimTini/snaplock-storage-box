"""Compare primitive catch construction to a supplied pre-change SCAD snapshot."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import subprocess
import time

import numpy as np
import trimesh


def surface_distance(source, target):
    # Inspect every vertex and face centre in both changed tooth regions, plus
    # deterministic whole-surface samples. This is a sampled bound, not Hausdorff.
    points = np.vstack((source.vertices, source.triangles_center,
                        trimesh.sample.sample_surface(source, 4000, seed=20261013)[0]))
    local = ((points[:, 1] >= 17.07) & (points[:, 1] <= 23.08) &
             ((points[:, 0] < 3.51) | (points[:, 0] > 24.49)))
    points = np.unique(points[local], axis=0)
    maximum = 0.0
    for start in range(0, len(points), 24):
        _, distances, _ = trimesh.proximity.closest_point_naive(target, points[start:start+24])
        maximum = max(maximum, float(distances.max()))
    return {'points': len(points), 'max_distance_mm': maximum}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('exports/catch-csg'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location('scad_audit', root / 'audit-scad.py')
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    baseline = args.baseline.resolve()
    current = audit.SCAD
    assert baseline != current and baseline.is_file(), 'Supply a separate pre-change snapshot'
    args.output.mkdir(parents=True, exist_ok=True)
    reference = audit.references()['latch']
    version = subprocess.run([str(audit.OPENSCAD), '--version'], check=True,
                             capture_output=True, text=True)
    report = {'baseline_sha256': hashlib.sha256(baseline.read_bytes()).hexdigest(),
              'scad_sha256': hashlib.sha256(current.read_bytes()).hexdigest(),
              'reference_stl_sha256': audit.HASH,
              'resolution_fn': 96,
              'openscad_version': (version.stdout + version.stderr).strip(),
              'trimesh_version': trimesh.__version__, 'numpy_version': np.__version__,
              'timing_scope': 'process, render, mesh load and cleanup; three sequential runs per source',
              'surface_method': 'bidirectional tooth vertices, face centres and seeded surface samples; not Hausdorff',
              'variants': []}
    for thickness in (5, 6, 6.5):
        meshes, timings = {}, {}
        for name, source in [('baseline', baseline), ('current', current)]:
            audit.SCAD = source
            elapsed = []
            for repeat in range(3):
                start = time.perf_counter()
                mesh = audit.build('latch', args.output / f'{name}-{thickness}-{repeat}.stl',
                                   [f'latch_thickness={thickness}', '$fn=96'])
                elapsed.append(time.perf_counter() - start)
                assert mesh.is_volume and len(mesh.split()) == 1, 'Expected one closed latch'
            meshes[name] = mesh
            timings[name] = {'seconds': elapsed, 'median_seconds': statistics.median(elapsed)}
        old, new = meshes['baseline'], meshes['current']
        common = trimesh.boolean.intersection([old, new], engine='manifold').volume
        row = {'thickness_mm': thickness, 'timings': timings,
               'volume_mm3': float(new.volume), 'faces': len(new.faces),
               'bounds_error_vs_baseline_mm': float(np.abs(old.bounds-new.bounds).max()),
               'symmetric_difference_vs_baseline_percent': float(100*(old.volume+new.volume-2*common)/old.volume),
               'old_to_new': surface_distance(old, new), 'new_to_old': surface_distance(new, old)}
        assert row['bounds_error_vs_baseline_mm'] < .01
        assert abs(row['symmetric_difference_vs_baseline_percent']) < .01
        assert max(row['old_to_new']['max_distance_mm'], row['new_to_old']['max_distance_mm']) < .01
        if thickness == 6:
            common = trimesh.boolean.intersection([new, reference], engine='manifold').volume
            row['symmetric_difference_vs_stl_percent'] = float(100*(new.volume+reference.volume-2*common)/reference.volume)
            row['bounds_error_vs_stl_mm'] = float(np.abs(new.bounds-reference.bounds).max())
            assert abs(row['symmetric_difference_vs_stl_percent']) < .1
            assert row['bounds_error_vs_stl_mm'] < .02
        report['variants'].append(row)
        (args.output / 'audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps(row), flush=True)


if __name__ == '__main__':
    main()
