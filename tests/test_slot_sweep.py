"""Independent measured-arc and elliptical-translation checks for the Sweep probe."""
import importlib.util
import math
from pathlib import Path
import unittest
from types import SimpleNamespace

PATH = Path(__file__).resolve().parents[1] / 'fusion/SlotSweepTest/SlotSweepTest.py'
spec = importlib.util.spec_from_file_location('slot_sweep', PATH)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class SlotSweep(unittest.TestCase):
    def test_fix_constant_sketch_also_locks_independent_points(self):
        class AlreadyFixed:
            @property
            def isFixed(self):
                return True
            @isFixed.setter
            def isFixed(self,value):
                raise AssertionError('Already fixed origin must be left alone')
        class ConstrainedOrigin(AlreadyFixed):
            isFullyConstrained = True
            @property
            def isFixed(self):
                return False
            @isFixed.setter
            def isFixed(self,value):
                raise AssertionError('Implicitly constrained origin must be left alone')
        curve = SimpleNamespace(isFixed=False,isFullyConstrained=False)
        points = [SimpleNamespace(isFixed=False,isFullyConstrained=False) for _ in range(3)]
        sketch = SimpleNamespace(sketchCurves=[curve],sketchPoints=[AlreadyFixed(),ConstrainedOrigin(),*points])
        probe.fix_constant_sketch(sketch)
        self.assertTrue(curve.isFixed)
        self.assertTrue(all(point.isFixed for point in points))

    def test_ellipse_parameter_angles_trace_short_right_branch_from_bottom(self):
        start,sweep = probe.path_angles()
        for i in range(41):
            angle = start+sweep*i/40
            x = .976+1.488*math.sin(angle)
            z = 4+5*math.cos(angle)
            self.assertTrue(-1e-12 <= z <= 8+1e-12)
            self.assertGreater(x,.976)
            expected = probe.surface_point(8,min(8,max(0,z)),0)
            self.assertAlmostEqual(x,expected[0])
        self.assertAlmostEqual(4+5*math.cos(start),0)
        self.assertAlmostEqual(4+5*math.cos(start+sweep),8)

    def test_reference_passes_measured_arc_points_and_ellipse(self):
        for thickness in (5, 6, 6.5):
            for z in (0, thickness/4, thickness/2, thickness):
                d = 5 - math.sqrt(25 - (z-thickness/2)**2)
                c = 2.847 - .2976*d
                for local_x, y in ((-.383,15.751),(-.4699,16.2434),(0,16.5724)):
                    self.assertLess(probe.reference_residual((c+local_x,y,z), thickness), 1e-9)
                x, y, height = probe.surface_point(thickness,z,0)
                self.assertAlmostEqual(((x-.976)/1.488)**2+((z-thickness/2)/5)**2,1)
                self.assertAlmostEqual(y,15.751)
                self.assertEqual(height,z)

    def test_reference_detects_rotation_and_outside_patch(self):
        point = probe.surface_point(6,1.3,.4)
        self.assertLess(probe.reference_residual(point,6),1e-9)
        self.assertGreater(probe.reference_residual((point[0]+.05,point[1],point[2]),6),.01)
        self.assertGreater(probe.reference_residual((point[0],point[1],-.2),6),.2)

    def test_profile_is_rigid_translation_across_height(self):
        for fraction in (0,.25,.5,.75,1):
            a=probe.surface_point(6,0,fraction)
            b=probe.surface_point(6,3,fraction)
            self.assertAlmostEqual(b[0]-a[0],.2976)
            self.assertEqual(b[1],a[1])


if __name__ == '__main__':
    unittest.main()
