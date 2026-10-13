import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace as NS
from tempfile import TemporaryDirectory
import unittest

spec = importlib.util.spec_from_file_location('export_model', Path(__file__).resolve().parents[1] /
                                            'fusion/SnaplockStorageBox/SnaplockStorageBox.py')
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class FusionExport(unittest.TestCase):
    def test_manifest_matches_four_files_and_current_source(self):
        bodies = [NS(name=name) for name in ('Body', 'Lid', 'Latch', 'Latch 2')]
        options = []
        def create(body, filename):
            opt = NS(filename=filename, body=body)
            options.append(opt)
            return opt
        def execute(opt):
            Path(opt.filename).write_bytes(opt.body.name.encode())
            return True
        design = NS(rootComponent=NS(bRepBodies=bodies),
                    userParameters=NS(itemByName=lambda name:NS(value=model.DEFAULTS[name]/10)),
                    exportManager=NS(createSTLExportOptions=create, execute=execute))
        fusion = NS(DistanceUnits=NS(MillimeterDistanceUnits=1),
                    MeshRefinementSettings=NS(MeshRefinementHigh=2))
        with TemporaryDirectory() as temp:
            path = model.export_meshes(design, fusion, Path(temp))
            data = json.loads(path.read_text())
            self.assertEqual(set(data['parts']), {'Body', 'Lid', 'Latch', 'Latch 2'})
            self.assertEqual(len(data['script_sha256']), 64)
            self.assertEqual(data['parameters_mm'],model.DEFAULTS)
            for row in data['parts'].values():
                self.assertTrue((Path(temp) / row['file']).is_file())
                self.assertEqual(len(row['sha256']), 64)
        self.assertEqual(len(options), 4)
        for opt in options:
            self.assertEqual(opt.unitType, 1)
            self.assertAlmostEqual(opt.surfaceDeviation, .0005)

    def test_failed_export_does_not_create_success_manifest(self):
        design = NS(rootComponent=NS(bRepBodies=[NS(name='Body')]),
                    exportManager=NS(createSTLExportOptions=lambda *a: NS(), execute=lambda *a: False))
        fusion = NS(DistanceUnits=NS(MillimeterDistanceUnits=1),
                    MeshRefinementSettings=NS(MeshRefinementHigh=2))
        with TemporaryDirectory() as temp:
            with self.assertRaises(RuntimeError):
                model.export_meshes(design, fusion, Path(temp))
            self.assertFalse((Path(temp) / 'manifest.json').exists())
