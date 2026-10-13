"""World-Y placement is independent of plane and sketch normal conventions."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock


SCRIPT = Path(__file__).resolve().parents[1] / 'fusion/SnaplockStorageBox/SnaplockStorageBox.py'
spec = importlib.util.spec_from_file_location('latch_orientation', SCRIPT)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class LatchOrientationTests(unittest.TestCase):
    def native(self, plane_y, sketch_y):
        placements, extrusions = [], []
        body = object()
        bodies = NS(count=1, item=lambda i: body)
        result = NS(bodies=bodies)
        sketch = NS(xDirection=NS(crossProduct=lambda other: NS(x=0, y=sketch_y, z=0)),
                    yDirection=object())
        def section(base, offset, *args):
            placements.append(float(offset.replace(' mm', '')) * plane_y)
            return sketch
        def extrude(sketch, distance, operation, name, **kwargs):
            extrusions.append((name, kwargs.get('negative', False)))
            return result
        native = NS(comp=NS(xZConstructionPlane=NS(geometry=NS(normal=NS(x=0, y=plane_y, z=0))),
                            xYConstructionPlane=object()),
                    fusion=NS(FeatureOperations=NS(NewBodyFeatureOperation=0, JoinFeatureOperation=1,
                                                    IntersectFeatureOperation=2)),
                    ellipse=section, circle=section, extrude=extrude,
                    loft=Mock(return_value=result), rectangle=Mock(return_value=sketch),
                    combine=Mock(), mirror=Mock(return_value=result), progress=Mock())
        return native, placements, extrusions

    def test_world_y_positions_and_core_direction_for_both_normals(self):
        for plane_y in (-1, 1):
            for sketch_y in (-1, 1):
                with self.subTest(plane_y=plane_y, sketch_y=sketch_y):
                    native, placements, extrusions = self.native(plane_y, sketch_y)
                    model.build_latch_teeth(native, object(), object())
                    self.assertEqual(placements, [17.0724, 18.0724, 22.0724, 23.0724])
                    core_negative = next(negative for name, negative in extrusions if name == 'Catch R5 core')
                    self.assertEqual(core_negative, sketch_y < 0)
                    native.progress.assert_called()

    def test_non_xz_plane_is_rejected_before_creating_sections(self):
        native, placements, extrusions = self.native(.5, 1)
        with self.assertRaisesRegex(RuntimeError, 'normal'):
            model.build_latch_teeth(native, object(), object())
        self.assertEqual(placements, [])


if __name__ == '__main__':
    unittest.main()
