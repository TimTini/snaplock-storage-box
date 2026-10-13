"""Hybrid slot preserves parametric front sections and consumes its tool bodies."""
import importlib.util
import math
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock

SCRIPT = Path(__file__).resolve().parents[1] / 'fusion/SnaplockStorageBox/SnaplockStorageBox.py'
spec = importlib.util.spec_from_file_location('hybrid_model', SCRIPT)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def mm(expression, thickness):
    return eval(expression.replace(' mm', '').replace('^', '**'),
                {'__builtins__': {}, 'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'asin': math.asin, 'latch_thickness': thickness})


class SlotHybrid(unittest.TestCase):
    def test_section_locations_and_front_boundary_follow_thickness(self):
        self.assertEqual(model.SLOT_SECTION_COUNT, 8)
        for thickness in (5, 6, 6.5):
            for index in range(model.SLOT_SECTION_COUNT):
                fraction = index/(model.SLOT_SECTION_COUNT-1)
                z, coords, arcs = model.slot_front_section(fraction)
                height = mm(z, thickness)
                expected_height = thickness/2+5*math.sin(math.asin(thickness/10)*(2*fraction-1))
                self.assertAlmostEqual(height, expected_height)
                d = 5-math.sqrt(25-(height-thickness/2)**2)
                self.assertAlmostEqual(mm(coords[0][1], thickness), 7.9971-d)
                self.assertAlmostEqual(mm(coords[4][0], thickness), 2.847-.2976*d)
                self.assertAlmostEqual(mm(coords[-2][0], thickness), .5+d)
                self.assertEqual(set(arcs), {3, 5})
                self.assertTrue(all(math.isfinite(mm(value, thickness)) for point in coords for value in point))

    def test_tool_join_mirror_and_cut_keep_only_latch(self):
        latch, tail, front, mirrored = [NS(name=name) for name in ('Latch', 'Tail', 'Front', 'Mirror')]
        bodies = [latch]
        result = lambda body: NS(bodies=NS(item=lambda i: body))
        def extrude(*args):
            bodies.append(tail)
            return result(tail)
        def loft(*args):
            bodies.append(front)
            return result(front)
        def combine(target, tools, operation, name):
            for tool in tools:
                bodies.remove(tool)
        def mirror(*args):
            bodies.append(mirrored)
        native = NS(comp=NS(xYConstructionPlane=object(), bRepBodies=bodies),
                    fusion=NS(FeatureOperations=NS(NewBodyFeatureOperation=0, JoinFeatureOperation=1,
                                                    CutFeatureOperation=2)),
                    profile=Mock(side_effect=lambda *a: a[4]), extrude=Mock(side_effect=extrude),
                    section_loft=Mock(side_effect=loft), combine=Mock(side_effect=combine),
                    mirror=Mock(side_effect=mirror), progress=Mock())
        symmetry = object()
        model.build_latch_relief(native, latch, symmetry)
        self.assertEqual(bodies, [latch])
        self.assertEqual(native.profile.call_count, 9)
        sections = native.section_loft.call_args.args[0]
        self.assertEqual(len(sections), 8)
        offsets = [call.args[1] for call in native.profile.call_args_list[1:]]
        self.assertEqual(offsets[0], '0 mm')
        self.assertEqual(offsets[-1], 'latch_thickness')
        for thickness in (5, 6, 6.5):
            for index, offset in enumerate(offsets):
                expected = thickness/2+5*math.sin(math.asin(thickness/10)*(2*index/7-1))
                self.assertAlmostEqual(mm(offset, thickness), expected)
        tail_call = native.profile.call_args_list[0]
        self.assertEqual(tail_call.args[2][0], ('3.5 mm', '17.0714 mm'))
        self.assertEqual(tail_call.args[2][-1], ('3.5 mm', '17.0724 mm'))
        self.assertEqual(set(tail_call.args[4]), {2, 4})
        self.assertEqual(native.mirror.call_args.args[:2], ([front], symmetry))
        self.assertEqual(native.combine.call_args_list[0].args[:2], (front, [tail]))
        self.assertEqual(native.combine.call_args_list[-1].args[:2], (latch, [front, mirrored]))
        self.assertEqual(native.combine.call_args_list[-1].args[2], 2)
        native.progress.assert_called()


if __name__ == '__main__':
    unittest.main()
