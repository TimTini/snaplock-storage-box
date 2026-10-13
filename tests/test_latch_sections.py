"""Measured relief changes across thickness, rather than a constant extrusion."""
import importlib.util
import math
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'fusion/SnaplockStorageBox/SnaplockStorageBox.py'
spec = importlib.util.spec_from_file_location('latch_model', SCRIPT)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def mm(expression, thickness=6):
    return eval(expression.replace(' mm', '').replace('^', '**').replace('latch_thickness', str(thickness)),
                {'__builtins__': {}, 'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'asin': math.asin})


class LatchSections(unittest.TestCase):
    def test_teeth_and_relief_follow_measured_middle_and_flat_faces(self):
        for fraction, d in [(0, 1), (.5, 0), (1, 1)]:
            z, slot, arcs = model.slot_front_section(fraction)
            self.assertAlmostEqual(mm(slot[-3][0]), 1.5 + 1.35*d, places=7)
            self.assertAlmostEqual(mm(slot[0][1]), 7.9971-d, places=7)
            self.assertAlmostEqual(mm(slot[4][0]), 2.847-.2976*d, places=7)
            self.assertEqual(len(arcs), 2)
            self.assertAlmostEqual(mm(slot[-2][0]), .5+d, places=7)
            self.assertAlmostEqual(mm(slot[-1][1]), 18.0724, places=7)

    def test_sections_remain_symmetric_and_valid_at_supported_thicknesses(self):
        for thickness in (5, 6, 6.5):
            for fraction in (0, .125, .25, .5):
                left = model.slot_front_section(fraction)
                right = model.slot_front_section(1-fraction)
                for a, b in zip(left[1], right[1]):
                    for x, y in zip(a, b):
                        self.assertTrue(math.isfinite(mm(x, thickness)))
                        self.assertAlmostEqual(mm(x, thickness), mm(y, thickness), places=8)

    def test_latch_x_extent_is_sphere_tips_not_slot_overhang(self):
        # Slot profiles start at X=-2; mirrored Cut of that loft grew bounds to 30.
        p = model.DEFAULTS
        self.assertEqual(20.5 + 2 * p['latch_ball_radius'], 28.0)
        self.assertAlmostEqual(mm(model.slot_front_section(0)[1][0][0]), -2)
        source = SCRIPT.read_text(encoding='utf8')
        self.assertIn("NewBodyFeatureOperation, 'Spring relief tool'", source)
        self.assertIn("CutFeatureOperation, 'Spring relief cuts'", source)
        self.assertNotIn("CutFeatureOperation, 'Spring relief thickness loft'", source)


if __name__ == '__main__':
    unittest.main()
