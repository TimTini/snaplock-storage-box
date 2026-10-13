"""Audit the intended analytic tooth against the 25-section SCAD reference.

This is an offline boundary/mesh check. Fusion's two-section Loft correspondence
and native recompute are verified separately by exporting and audit-fusion.py.
"""

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('latch', ROOT / 'fusion/SnaplockStorageBox/SnaplockStorageBox.py')
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def reference_ring(z, thickness):
    coords = model.latch_sections(z / thickness)[0]
    return [[eval(e.replace(' mm', '').replace('^', '**'),
                  {'__builtins__': {}, 'sqrt': math.sqrt, 'latch_thickness': thickness})
             for e in pair] for pair in coords]


def analytic_ring(z, thickness):
    root = math.sqrt(25 - (z - thickness / 2) ** 2)
    shoulder = 8.25 - 6.75 * root / 5
    tip = 5.5 - root
    return [[shoulder, 17.0724], [tip, 18.0724], [tip, 22.0724],
            [shoulder, 23.0724], [3.5, 23.0724], [3.5, 17.0724]]


def mesh(rings, zs):
    vertices = [[x, y, z] for ring, z in zip(rings, zs) for x, y in ring]
    n = len(rings[0])
    faces = []
    for j in range(1, n - 1):
        faces.extend([[0, j + 1, j], [(len(rings) - 1)*n,
                      (len(rings) - 1)*n + j, (len(rings) - 1)*n + j + 1]])
    for i in range(len(rings) - 1):
        for j in range(n):
            a, b = i*n + j, i*n + (j+1) % n
            faces.extend([[a, b, b+n], [a, b+n, a+n]])
    result = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    result.fix_normals()
    if not result.is_volume:
        raise RuntimeError('Expected a closed positive-volume tooth mesh')
    return result


def main():
    report = {'scope': 'offline intended analytic boundary; native Fusion Loft remains separate',
              'sampled_reference_sections': 25, 'analytic_mesh_sections': 481,
              'cases': []}
    for thickness in (5, 6, 6.5):
        fine_z = np.linspace(0, thickness, 481)
        equation_error = max(abs(a - b) for z in fine_z
                             for p, q in zip(reference_ring(z, thickness), analytic_ring(z, thickness))
                             for a, b in zip(p, q))
        old_z = np.linspace(0, thickness, 25)
        old = mesh([reference_ring(z, thickness) for z in old_z], old_z)
        new = mesh([analytic_ring(z, thickness) for z in fine_z], fine_z)
        common = trimesh.boolean.intersection([old, new], engine='manifold').volume
        symmetric = max(0, old.volume + new.volume - 2 * common)
        # Piecewise-linear reference deviates slightly from the continuous arc.
        max_sampled_error = 0
        for z in fine_z:
            i = min(int(z / thickness * 24), 23)
            blend = (z - old_z[i]) / (old_z[i+1] - old_z[i])
            approx = (1-blend)*np.array(reference_ring(old_z[i], thickness)) + blend*np.array(reference_ring(old_z[i+1], thickness))
            max_sampled_error = max(max_sampled_error, float(np.abs(approx - analytic_ring(z, thickness)).max()))
        row = {'thickness_mm': thickness, 'analytic_equation_error_mm': equation_error,
               'sampled_boundary_max_difference_mm': max_sampled_error,
               'reference_tooth_volume_mm3': float(old.volume),
               'analytic_tooth_volume_mm3': float(new.volume),
               'symmetric_difference_mm3': float(symmetric),
               'symmetric_difference_percent_of_tooth': float(100*symmetric/old.volume)}
        report['cases'].append(row)
        if equation_error > 1e-10 or max_sampled_error > .01:
            raise RuntimeError('Intended analytic boundary exceeds offline tolerance: ' + str(row))
    output = ROOT / 'docs/validation/latch-analytic-offline.json'
    output.write_text(json.dumps(report, indent=2), encoding='utf8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
