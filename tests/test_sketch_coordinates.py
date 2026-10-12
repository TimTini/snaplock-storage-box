import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'fusion/SnaplockStorageBox/SnaplockStorageBox.py'
spec = importlib.util.spec_from_file_location('snaplock_coordinates', SCRIPT)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class SketchCoordinatesTests(unittest.TestCase):
    def setUp(self):
        self.native = model.Native.__new__(model.Native)
        self.native.comp = SimpleNamespace(xYConstructionPlane=object(), yZConstructionPlane=object())

    def sketch(self, x, y):
        return SimpleNamespace(
            xDirection=SimpleNamespace(x=x[0], y=x[1], z=x[2]),
            yDirection=SimpleNamespace(x=y[0], y=y[1], z=y[2]))

    def test_xy_keeps_parameter_expressions(self):
        sketch = self.sketch((1, 0, 0), (0, 1, 0))
        self.assertEqual(self.native.coordinates(sketch, self.native.comp.xYConstructionPlane,
                         ('length - wall', 'body_height')), ('length - wall', 'body_height'))

    def test_yz_maps_height_to_negative_sketch_x(self):
        sketch = self.sketch((0, 0, -1), (0, 1, 0))
        self.assertEqual(self.native.coordinates(sketch, self.native.comp.yZConstructionPlane,
                         ('-4.75 mm', 'body_height')), ('-(body_height)', '-4.75 mm'))

    def test_yz_alternate_orientation_uses_actual_basis(self):
        sketch = self.sketch((0, 1, 0), (0, 0, 1))
        self.assertEqual(self.native.coordinates(sketch, self.native.comp.yZConstructionPlane,
                         ('-4.75 mm', 'body_height')), ('-4.75 mm', 'body_height'))

    def test_rear_web_overlaps_socket_after_coordinate_mapping(self):
        # Interior point at x=21.5, Y=-4.75, Z=52 lies in the R4.25
        # web head and in the sphere at (25.9,-4.75,52), R5.
        sketch = self.sketch((0, 0, -1), (0, 1, 0))
        mapped = self.native.coordinates(sketch, self.native.comp.yZConstructionPlane,
                                         ('-4.75', '52'))
        u, v = (eval(expression, {'__builtins__': {}}) for expression in mapped)
        world_y, world_z = v, -u
        self.assertLess((world_y + 4.75)**2 + (world_z - 52)**2, 4.25**2)
        self.assertLess((21.5 - 25.9)**2 + (world_y + 4.75)**2 + (world_z - 52)**2, 5**2)
        # The original untransformed (Y,Z) input places the web at Y=52,Z=4.75.
        self.assertGreater((52 + 4.75)**2 + (4.75 - 52)**2, 5**2)


if __name__ == '__main__':
    unittest.main()
