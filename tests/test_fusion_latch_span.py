"""Parameter dependency and construction checks; native solver is separate."""
import importlib.util
import math
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock
import unittest

spec = importlib.util.spec_from_file_location('span_model', Path(__file__).resolve().parents[1] /
                                            'fusion/SnaplockStorageBox/SnaplockStorageBox.py')
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class FusionLatchSpan(unittest.TestCase):
    def test_lid_height_keeps_mating_anchors_and_catch_world_height(self):
        for height in (11.7, 15, 20, 50, 233.1, 245.5):
            p = dict(model.DEFAULTS, lid_height=height)
            d = model.dimensions(p)
            self.assertEqual(d['mount_centres'], d['lid_mount_centres'])
            delta = eval(model.DERIVED['latch_span_delta'].replace(' mm',''), {}, p)
            self.assertAlmostEqual(p['body_height'] + height - (18.0724 + delta),
                                   p['body_height'] - 3.0724)

    def test_relief_reuses_eight_sections_and_links_both_windows(self):
        feature = lambda: NS(bodies=NS(item=lambda i: object()))
        n = NS(comp=NS(xYConstructionPlane=object(), bRepBodies=[NS(name='Latch')]+
                      [NS(name='Tool') for _ in range(4)]),
               fusion=NS(FeatureOperations=NS(NewBodyFeatureOperation=0,
                         JoinFeatureOperation=1, IntersectFeatureOperation=2, CutFeatureOperation=3)),
               profile=Mock(), rectangle=Mock(), extrude=Mock(side_effect=lambda *a,**k:feature()),
               section_loft=Mock(side_effect=lambda *a,**k:feature()), combine=Mock(),
               mirror=Mock(), translate=Mock(), progress=Mock())
        model.build_latch_relief(n, object(), object())
        self.assertEqual(n.section_loft.call_count, 2)
        self.assertEqual(len(n.section_loft.call_args_list[0].args[0]), 8)
        self.assertEqual(n.section_loft.call_args_list[0].args[0],
                         n.section_loft.call_args_list[1].args[0])
        self.assertEqual([c.args[2] for c in n.translate.call_args_list],
                         ['15 mm','lid_height','-10 mm','-10 mm'])
        rectangles = ' '.join(str(c.args) for c in n.rectangle.call_args_list)
        self.assertIn('latch_relief_floor', rectangles)
        self.assertIn('latch_head_window_end', rectangles)
        for call in n.rectangle.call_args_list:
            self.assertEqual(call.args[3], 'latch_relief_floor + 10 mm')
            for floor in (-.001,7):
                coordinate=eval(call.args[3].replace(' mm',''),{}, {'latch_relief_floor':floor})
                self.assertGreater(coordinate,0)
                self.assertAlmostEqual(coordinate-10,floor)
        tail = n.profile.call_args_list[0].args[2]
        self.assertTrue(all('latch_span_delta' in y for x,y in tail))

    def test_profile_translation_preserves_curves_and_arc_radii(self):
        for thickness in (5,6,6.5):
            for index in range(model.SLOT_SECTION_COUNT):
                _, coords, arcs = model.slot_front_section(index/7)
                shifted, shifted_arcs = model.shift_profile_y(coords, arcs, '-15 mm')
                def number(expr):
                    return eval(expr.replace(' mm',''), {'__builtins__': {}},
                                {'latch_thickness':thickness, 'asin':math.asin,
                                 'sin':math.sin,'cos':math.cos,'sqrt':math.sqrt})
                for height in (11.7,15,20,233.1):
                    for (x,y),(sx,sy) in zip(coords,shifted):
                        self.assertEqual(x,sx)
                        self.assertAlmostEqual(number(sy)+height,number(y)+height-15)
                for i,(mid,radius) in arcs.items():
                    moved, moved_radius = shifted_arcs[i]
                    self.assertEqual(radius,moved_radius)
                    self.assertAlmostEqual(number(moved[1])+15,number(mid[1]))


if __name__ == '__main__':
    unittest.main()
