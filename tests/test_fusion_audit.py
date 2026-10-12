import hashlib
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import trimesh

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fusion_audit', ROOT / 'audit-fusion.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class FusionAudit(unittest.TestCase):
    def test_translation_does_not_mask_scaling_or_missing_material(self):
        reference = trimesh.creation.box(extents=[10, 20, 30])
        mesh = reference.copy()
        mesh.apply_translation([48, 300, -20])
        row = audit.compare(mesh, reference)
        self.assertAlmostEqual(row['symmetric_difference_percent'], 0, places=5)
        self.assertAlmostEqual(row['bounds_error_mm'], 0, places=7)
        mesh.apply_scale(.9)
        row = audit.compare(mesh, reference)
        self.assertGreater(row['missing_mm3'], 1600)
        self.assertGreater(row['bounds_error_mm'], 2.9)

    def test_loader_rejects_stale_source_and_tampered_mesh(self):
        with TemporaryDirectory() as temp:
            directory = Path(temp)
            path = directory / 'body.stl'
            trimesh.creation.box().export(path)
            row = {'file': path.name, 'sha256': audit.sha(path)}
            manifest = {'script_sha256': 'old source', 'units': 'mm',
                        'parts': {name: row.copy() for name in ('Body', 'Lid', 'Latch', 'Latch 2')}}
            file = directory / 'manifest.json'
            file.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'another Python source'):
                audit.load_exports(directory)
            manifest['script_sha256'] = audit.sha(audit.SCRIPT)
            file.write_text(json.dumps(manifest))
            self.assertEqual(len(audit.load_exports(directory)[1]), 4)
            path.write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'STL hash mismatch'):
                audit.load_exports(directory)
