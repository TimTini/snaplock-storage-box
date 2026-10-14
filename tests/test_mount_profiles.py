"""Survey geometry checks independent of Fusion's sketch solver."""
import importlib.util
import math
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock

import numpy as np

spec = importlib.util.spec_from_file_location('mount_model', Path(__file__).resolve().parents[1] /
                                            'fusion/SnaplockStorageBox/SnaplockStorageBox.py')
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def mm(expression):
    return eval(expression.replace(' mm', ''), {'__builtins__': {}, 'sqrt': math.sqrt,
                                               **model.DEFAULTS})


class MountProfiles(unittest.TestCase):
    def test_lid_taper_has_numeric_separation_from_nearly_coincident_web(self):
        n = self.native()
        model.mount_make_lid_rear(n, 'mount_end')
        starts = [call for call in n.circle.call_args_list if call.args[-1]=='Lid lip taper start']
        ends = [call for call in n.circle.call_args_list if call.args[-1]=='Lid lip taper end']
        self.assertEqual(len(starts),1)
        self.assertEqual(len(ends),1)
        expected_start=9.486833-3.735*math.tan(math.radians(50))+.001
        expected_end=9.486833+.001*math.tan(math.radians(50))+.001
        for call,expected in zip((starts[0],ends[0]),(expected_start,expected_end)):
            actual=eval(call.args[4].replace(' mm','').replace(' deg',''),
                        {'__builtins__':{},'tan':lambda x:math.tan(math.radians(x))})
            self.assertAlmostEqual(actual,expected)

    def native(self):
        body = NS()
        feature = NS(bodies=NS(item=lambda index: body))
        return NS(comp=NS(xYConstructionPlane='XY', yZConstructionPlane='YZ'),
                  fusion=NS(FeatureOperations=NS(NewBodyFeatureOperation=0, CutFeatureOperation=1,
                                                 JoinFeatureOperation=2, IntersectFeatureOperation=3)),
                  profile=Mock(), circle=Mock(), rectangle=Mock(), combine=Mock(),
                  sphere=Mock(return_value=feature), extrude=Mock(return_value=feature),
                  loft=Mock(return_value=feature))

    def test_arc_radii_agree_with_fixed_endpoints_and_survey_midpoints(self):
        checked = 0
        for build in (model.mount_make_rear_body, model.mount_make_body_front,
                      model.mount_make_lid_rear, model.mount_make_lid_front):
            n = self.native()
            build(n, 'mount_end')
            for call in n.profile.call_args_list:
                if len(call.args) < 5 or not call.args[4]:
                    continue
                coords, arcs = call.args[2], call.args[4]
                for i, (mid, radius) in arcs.items():
                    checked += 1
                    points = np.array([[mm(v) for v in pair] for pair in
                                       (coords[i], mid, coords[(i+1) % len(coords)])])
                    delta = points[1:] - points[0]
                    center = np.linalg.solve(2*delta, (delta*delta).sum(axis=1))
                    measured = np.linalg.norm(center)
                    self.assertAlmostEqual(measured, mm(radius), delta=1e-5,
                                           msg=call.args[3])
        self.assertEqual(checked, 5)

    def test_body_front_annular_lip_axis_is_above_shell_top(self):
        n = self.native()
        model.mount_make_body_front(n, 'mount_end')
        lip_calls = [call for call in n.circle.call_args_list if 'lip' in call.args[-1].lower()]
        self.assertEqual(len(lip_calls), 3)
        for call in lip_calls:
            self.assertAlmostEqual(mm(call.args[2]), 126.15)
            self.assertAlmostEqual(mm(call.args[3]), 61)

    def test_pocket_barrel_uses_lower_chamfer_endpoint_profile(self):
        n = self.native()
        n.circle.side_effect = lambda *args: NS(name=args[-1])
        model.mount_make_body_front(n, 'mount_end')
        chamfer = next(c for c in n.loft.call_args_list if c.args[3]=='Front pocket lower chamfer')
        barrel = next(c for c in n.extrude.call_args_list if c.args[3]=='Front pocket barrel')
        self.assertIs(barrel.args[0], chamfer.args[1])
        self.assertEqual(barrel.args[1], '4.5 mm')
