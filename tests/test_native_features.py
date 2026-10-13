import importlib.util
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock

SCRIPT = Path(__file__).resolve().parents[1] / 'fusion/SnaplockStorageBox/SnaplockStorageBox.py'
spec = importlib.util.spec_from_file_location('snaplock_native', SCRIPT)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class NativeFeatureTests(unittest.TestCase):
    def test_profile_constrains_connected_geometry_after_creating_edges(self):
        # Model a solver which updates curve status when constraints are added.
        # Constraining loose points first leaves later-created lines stale/free.
        n = model.Native.__new__(model.Native)
        edges = []
        def solve(*args):
            for edge in edges:
                edge.isFullyConstrained = True
            return NS(parameter=NS(expression=''))
        def add_line(a, b):
            edge = NS(startSketchPoint=a, endSketchPoint=b, isFullyConstrained=False)
            edges.append(edge)
            return edge
        points = NS(add=lambda p: p)
        sketch = NS(originPoint=object(), sketchPoints=points, sketchCurves=NS(sketchLines=NS(addByTwoPoints=add_line)),
                    geometricConstraints=NS(addVerticalPoints=solve, addHorizontalPoints=solve),
                    sketchDimensions=NS(addOffsetDimension=solve), profiles=NS(count=1))
        n.comp = NS(sketches=NS(add=lambda plane: sketch))
        n.plane = lambda *args: object()
        n.coordinates = lambda sk, base, pair: pair
        n.point = lambda x, y, z: NS(x=x, y=y, z=z)
        n.cm = lambda expr: float(expr.replace(' mm', '')) / 10
        def require(sk):
            self.assertTrue(all(e.isFullyConstrained for e in edges[2:]),
                            'Connected profile lines must participate in constraint solving')
        n.require_constrained = require
        n.profile(object(), '0 mm', [('1.5 mm','0 mm'), ('26.5 mm','0 mm'),
                                    ('26.5 mm','32.9 mm'), ('1.5 mm','32.9 mm')], 'Latch plate')

    def test_unconstrained_sketch_reports_free_entities_and_constraints(self):
        n = model.Native.__new__(model.Native)
        messages = []
        n.progress = messages.append
        point = NS(objectType='SketchPoint', isFullyConstrained=False,
                   geometry=NS(x=.15, y=0, z=0),
                   geometricConstraints=NS(count=1), sketchDimensions=NS(count=0))
        curve = NS(objectType='SketchLine', isFullyConstrained=True)
        collection = lambda items: NS(count=len(items), item=lambda i: items[i])
        sketch = NS(name='Latch plate', isFullyConstrained=False,
                    sketchPoints=collection([point]), sketchCurves=collection([curve]),
                    geometricConstraints=NS(count=6), sketchDimensions=NS(count=6))
        with self.assertRaisesRegex(RuntimeError, 'Latch plate'):
            n.require_constrained(sketch)
        self.assertIn('point[0]', messages[0])
        self.assertIn('1.5', messages[0])
        self.assertIn('constraints', messages[0])

    def test_healthy_sketch_does_not_emit_failure_diagnostics(self):
        n = model.Native.__new__(model.Native)
        n.progress = Mock()
        n.require_constrained(NS(isFullyConstrained=True))
        n.progress.assert_not_called()

    def test_single_direction_pattern_overrides_second_direction_default(self):
        for seed_count in (1, 4):
            with self.subTest(seed_count=seed_count):
                n = model.Native.__new__(model.Native)
                def create_input(entities, axis, quantity, distance, mode):
                    return NS(quantityOne=quantity, quantityTwo='3')
                def add(inp):
                    return NS(instance_count=int(inp.quantityOne) * int(inp.quantityTwo))
                n.comp = NS(features=NS(rectangularPatternFeatures=NS(createInput=create_input, add=add)))
                n.fusion = NS(PatternDistanceType=NS(SpacingPatternDistanceType=0),
                              PatternComputeOptions=NS(IdenticalPatternCompute=0))
                n.objects = lambda items: items
                n.value = lambda value: value
                n.feature = lambda feature, name: feature
                result = n.pattern([object() for _ in range(seed_count)], object(), '48 mm', 'Pattern')
                self.assertEqual(result.instance_count, 2, 'Expected 2 x 1, not a 2 x 3 grid')

    def test_literal_zero_offset_reuses_origin_plane(self):
        n = model.Native.__new__(model.Native)
        n.value = lambda value: value
        planes = NS(createInput=Mock(), add=Mock())
        n.comp = NS(constructionPlanes=planes)
        base = object()
        self.assertIs(n.plane(base, '0 mm', 'Zero plane'), base)
        planes.createInput.assert_not_called()
        planes.add.assert_not_called()

    def test_parameter_currently_zero_keeps_associative_offset_plane(self):
        n = model.Native.__new__(model.Native)
        n._planes = []
        n.value = lambda value: value
        inp = NS(setByOffset=Mock(return_value=True))
        result = NS(name='', isLightBulbOn=True)
        n.comp = NS(constructionPlanes=NS(createInput=lambda: inp, add=lambda _: result))
        base = object()
        self.assertIs(n.plane(base, 'fit_clearance', 'Parametric offset'), result)
        inp.setByOffset.assert_called_once_with(base, 'fit_clearance')

    def test_reuses_only_matching_base_and_exact_offset_expression(self):
        n = model.Native.__new__(model.Native)
        n._planes = []
        n.value = lambda value: value
        inp = NS(setByOffset=Mock(return_value=True))
        planes = NS(createInput=Mock(return_value=inp),
                    add=Mock(side_effect=lambda _: NS(name='', isLightBulbOn=True)))
        n.comp = NS(constructionPlanes=planes)
        base, other = object(), object()
        first = n.plane(base, 'body_height - 10.5 mm', 'Chamfer end')
        self.assertIs(n.plane(base, 'body_height - 10.5 mm', 'Barrel start'), first)
        self.assertIsNot(n.plane(other, 'body_height - 10.5 mm', 'Other base'), first)
        self.assertIsNot(n.plane(base, 'body_height - 10 mm - 0.5 mm', 'Other expression'), first)
        self.assertEqual(planes.add.call_count, 3)
        self.assertEqual(first.name, 'Chamfer end')

    def test_plane_reuse_is_scoped_to_one_native_builder(self):
        base = object()
        inp = NS(setByOffset=Mock(return_value=True))
        planes = NS(createInput=Mock(return_value=inp),
                    add=Mock(side_effect=lambda _: NS(name='', isLightBulbOn=True)))
        builders = [model.Native.__new__(model.Native) for _ in range(2)]
        for n in builders:
            n._planes = []
            n.value = lambda value: value
            n.comp = NS(constructionPlanes=planes)
        self.assertIsNot(builders[0].plane(base, 'body_height', 'First document'),
                         builders[1].plane(base, 'body_height', 'Second document'))
        self.assertEqual(planes.add.call_count, 2)


if __name__ == '__main__':
    unittest.main()
