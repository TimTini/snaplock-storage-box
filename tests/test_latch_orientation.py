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
    def setUp(self):
        self.symmetry = NS(geometry=NS(origin=NS(x=1.4)))

    def native(self, plane_y, sketch_y, mirror_return_count=2, delta=0):
        placements, extrusions = [], []
        def solid(name, low_x, high_x):
            return NS(name=name, volume=1, preciseBoundingBox=NS(
                minPoint=NS(x=low_x, y=1.70724, z=0),
                maxPoint=NS(x=high_x, y=2.30724, z=.6)))
        body = solid('Catch source', .05, .35)
        copy = solid('Catch copy', 2.45, 2.75)
        plate = solid('Latch', .15, 2.65)
        component_bodies = [body, plate]
        bodies = NS(count=1, item=lambda i: body)
        result = NS(bodies=bodies)
        sketch = NS(xDirection=NS(crossProduct=lambda other: NS(x=0, y=sketch_y, z=0)),
                    yDirection=object())
        def section(base, offset, *args):
            placements.append(eval(offset.replace(' mm', ''), {'__builtins__': {}}, {'latch_span_delta': delta}) * plane_y)
            return sketch
        def extrude(sketch, distance, operation, name, **kwargs):
            extrusions.append((name, kwargs.get('negative', False)))
            return result
        def mirror(*args):
            component_bodies.append(copy)
            affected = [body, copy] if mirror_return_count == 2 else ([copy] if mirror_return_count == 1 else [])
            return NS(bodies=NS(count=len(affected), item=lambda i: affected[i]))
        native = NS(comp=NS(xZConstructionPlane=NS(geometry=NS(normal=NS(x=0, y=plane_y, z=0))),
                            xYConstructionPlane=object(), bRepBodies=component_bodies),
                    fusion=NS(FeatureOperations=NS(NewBodyFeatureOperation=0, JoinFeatureOperation=1,
                                                    IntersectFeatureOperation=2)),
                    ellipse=section, circle=section, extrude=extrude,
                    loft=Mock(return_value=result), rectangle=Mock(return_value=sketch),
                    combine=Mock(), mirror=Mock(side_effect=mirror), progress=Mock())
        return native, placements, extrusions

    def test_world_y_positions_and_core_direction_for_both_normals(self):
        for plane_y in (-1, 1):
            for sketch_y in (-1, 1):
                with self.subTest(plane_y=plane_y, sketch_y=sketch_y):
                    native, placements, extrusions = self.native(plane_y, sketch_y)
                    model.build_latch_teeth(native, object(), self.symmetry)
                    self.assertEqual(placements, [17.0724, 18.0724, 22.0724, 23.0724])
                    core_negative = next(negative for name, negative in extrusions if name == 'Catch R5 core')
                    self.assertEqual(core_negative, sketch_y < 0)
                    native.progress.assert_called()

    def test_non_xz_plane_is_rejected_before_creating_sections(self):
        native, placements, extrusions = self.native(.5, 1)
        with self.assertRaisesRegex(RuntimeError, 'normal'):
            model.build_latch_teeth(native, object(), self.symmetry)
        self.assertEqual(placements, [])

    def test_catch_sections_follow_lid_height_for_both_plane_normals(self):
        for height in (11.7, 20, 50, 233.1, 245.5):
            for normal in (-1, 1):
                native, placements, _ = self.native(normal, normal, delta=height-15)
                model.build_latch_teeth(native, object(), self.symmetry)
                for actual, baseline in zip(placements, (17.0724,18.0724,22.0724,23.0724)):
                    self.assertAlmostEqual(actual, baseline + height - 15)

    def test_mirror_selects_geometric_copy_not_feature_collection_count(self):
        for returned_count in (0, 1, 2):
            with self.subTest(returned_count=returned_count):
                native, _, _ = self.native(1, 1, returned_count)
                latch = object()
                model.build_latch_teeth(native, latch, self.symmetry)
                target, tools = native.combine.call_args.args[:2]
                self.assertIs(target, latch)
                self.assertEqual([body.name for body in tools], ['Catch source', 'Catch copy'])

    def test_missing_ambiguous_or_wrong_volume_copy_is_rejected(self):
        for mode in ('missing', 'duplicate', 'wrong_volume'):
            with self.subTest(mode=mode):
                native, _, _ = self.native(1, 1)
                create_mirror = native.mirror.side_effect
                def altered_mirror(*args):
                    result = create_mirror(*args)
                    copy = native.comp.bRepBodies[-1]
                    if mode == 'missing':
                        native.comp.bRepBodies.pop()
                    elif mode == 'duplicate':
                        native.comp.bRepBodies.append(NS(name='Duplicate', volume=copy.volume,
                                                         preciseBoundingBox=copy.preciseBoundingBox))
                    else:
                        copy.volume *= 2
                    return result
                native.mirror.side_effect = altered_mirror
                with self.assertRaisesRegex(RuntimeError, 'geometric mirrored catch body'):
                    model.build_latch_teeth(native, object(), self.symmetry)


if __name__ == '__main__':
    unittest.main()
