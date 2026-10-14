import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'fusion/SnaplockStorageBox/SnaplockStorageBox.py'

class DimensionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = None
        if SCRIPT.exists():
            spec = importlib.util.spec_from_file_location('snaplock', SCRIPT)
            cls.model = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.model)

    def model_api(self):
        self.assertIsNotNone(self.model, 'Fusion script with dimensional validation is not implemented')
        return self.model

    def test_source_main_shell_dimensions(self):
        m = self.model_api()
        d = m.dimensions(m.DEFAULTS)
        self.assertAlmostEqual(d['inner_length'], 231.85, places=4)
        self.assertAlmostEqual(d['inner_width'], 117.15, places=4)
        self.assertAlmostEqual(d['outer_bevel_height'], 8.660254, places=4)
        self.assertAlmostEqual(d['body_inner_bevel_top'], 10.140639, places=4)
        self.assertAlmostEqual(d['lid_inner_bevel_top'], 9.464102, places=4)

    def test_resize_keeps_mechanical_interface_dimensions(self):
        m = self.model_api()
        p = dict(m.DEFAULTS, length=280, width=155, body_height=70)
        d = m.dimensions(p)
        self.assertAlmostEqual(d['inner_length'], 274)
        self.assertAlmostEqual(d['mount_spacing'], 214.2)
        self.assertEqual(p['pin_radius'], m.DEFAULTS['pin_radius'])
        self.assertEqual(p['latch_thickness'], 6)

    def test_invalid_dimensions_fail_before_fusion_document(self):
        m = self.model_api()
        for update in ({'wall': 0}, {'corner_radius': 4}, {'body_floor': 0},
                       {'body_height': 8}, {'length': 60}, {'fit_clearance': -0.1},
                       {'latch_thickness': 0}, {'latch_thickness': 10}, {'pin_radius': 3},
                       {'body_inner_bevel': 9}, {'bottom_bevel': 0.1}, {'width': float('nan')}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                m.dimensions(dict(m.DEFAULTS, **update))

    def test_lid_and_body_share_mount_centres(self):
        m = self.model_api()
        for length in (237.85, 280):
            d = m.dimensions(dict(m.DEFAULTS, length=length))
            self.assertEqual(d['mount_centres'], [32.9, length-32.9])
            self.assertAlmostEqual(d['mount_spacing'], length-65.8)
            self.assertAlmostEqual(d['lid_mount_centres'][0], 32.9)
            self.assertAlmostEqual(d['lid_mount_centres'][1], length-32.9)

if __name__ == '__main__':
    unittest.main()
