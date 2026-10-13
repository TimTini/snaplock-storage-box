import importlib.util
from pathlib import Path
from types import SimpleNamespace as NS
import sys
import unittest
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).resolve().parents[1] / 'fusion/SnaplockStorageBox/SnaplockStorageBox.py'
spec = importlib.util.spec_from_file_location('snaplock_single', SCRIPT)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class Collection(list):
    @property
    def count(self):
        return len(self)

    def item(self, index):
        return self[index]

    def itemByName(self, name):
        return next((item for item in self if item.name == name), None)


class RootComponent(NS):
    @property
    def name(self):
        return 'Document name'

    @name.setter
    def name(self, value):
        raise RuntimeError('root component name cannot be changed')


class BodyWrapper(NS):
    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other


class SingleComponentTests(unittest.TestCase):
    def setUp(self):
        self.fusion = NS(Feature=type('Feature', (), {}),
                         FeatureHealthStates=NS(HealthyFeatureHealthState=0))
        self.root = RootComponent(allOccurrences=Collection(), sketches=Collection(), bRepBodies=Collection())
        params = NS(itemByName=lambda name: NS(value=model.DEFAULTS[name] / 10))
        self.design = NS(rootComponent=self.root, userParameters=params,
                         computeAll=lambda: True, timeline=Collection())
        self.modules = patch.dict(sys.modules, {'adsk': NS(fusion=self.fusion), 'adsk.fusion': self.fusion})
        self.modules.start()
        self.addCleanup(self.modules.stop)

    def body(self, name, extents):
        return BodyWrapper(name=name, isSolid=True, volume=1,
                  preciseBoundingBox=NS(minPoint=NS(x=0, y=0, z=0),
                     maxPoint=NS(**dict(zip('xyz', [v / 10 for v in extents])))))

    def populate(self):
        self.root.bRepBodies.extend([
            self.body('Body', [237.85, 140.15, 56.25]),
            self.body('Lid', [237.85, 140.40, 19.5]),
            self.body('Latch', [28, 31.835144, 6]),
            self.body('Latch 2', [28, 31.835144, 6])])
        for name, x, y, major in [
                ('Catch front shoulder ellipse', 8.25, 17.0724, 6.75),
                ('Catch R5 front section', 5.5, 18.0724, 5),
                ('Catch R5 rear section', 5.5, 22.0724, 5),
                ('Catch rear shoulder ellipse', 8.25, 23.0724, 6.75)]:
            curve = NS(worldGeometry=NS(center=NS(x=x/10, y=y/10, z=.3)),
                       majorAxisRadius=major/10, minorAxisRadius=.5, radius=.5)
            self.root.sketches.append(NS(name=name, isFullyConstrained=True,
                sketchCurves=NS(sketchEllipses=Collection([curve]), sketchCircles=Collection([curve]))))

    def test_four_root_bodies_pass_without_occurrences(self):
        self.populate()
        self.assertEqual(len(model.check_model(self.design)), 8)

    def test_stale_analytic_section_height_is_rejected(self):
        self.populate()
        self.root.sketches[0].sketchCurves.sketchEllipses[0].worldGeometry.center.z = .25
        with self.assertRaisesRegex(RuntimeError, 'analytic section mismatch'):
            model.check_model(self.design)

    def test_extra_tool_body_is_rejected(self):
        self.populate()
        self.root.bRepBodies.append(self.body('Leftover tool', [1, 1, 1]))
        with self.assertRaisesRegex(RuntimeError, 'four named solid bodies'):
            model.check_model(self.design)

    def test_second_latch_bounds_are_checked(self):
        self.populate()
        self.root.bRepBodies[-1].preciseBoundingBox.maxPoint.x = 9
        with self.assertRaisesRegex(RuntimeError, 'Latch 2: unexpected bounds'):
            model.check_model(self.design)

    def test_mount_pattern_and_combine_exclude_existing_parts(self):
        existing = BodyWrapper(name='Latch')
        shell = BodyWrapper(name='Body')
        bodies = Collection([existing, shell])
        def extrude(*args):
            body = BodyWrapper(name='web ' + str(len(bodies)))
            bodies.append(body)
            return NS(bodies=Collection([body]))
        def mirror(tools, *args):
            bodies.extend([BodyWrapper(name=body.name + ' mirror') for body in tools])
            # Simulate new wrappers after a feature updates the design.
            bodies[:] = [BodyWrapper(name=body.name) for body in bodies]
        def pattern(tools, *args):
            self.assertEqual(len(tools), 4)
            self.assertNotIn(existing, tools)
            self.assertNotIn(shell, tools)
            self.assertNotIn('Latch', {body.name for body in tools})
            self.assertNotIn('Body', {body.name for body in tools})
            bodies.extend([BodyWrapper(name=body.name + ' pattern') for body in tools])
        def combine(target, tools, *args):
            self.assertIs(target, shell)
            self.assertEqual(len(tools), 8)
            self.assertNotIn(existing, tools)
            self.assertNotIn(shell, tools)
            self.assertNotIn('Latch', {body.name for body in tools})
            self.assertNotIn('Body', {body.name for body in tools})
        n = NS(comp=NS(yZConstructionPlane=object(), xConstructionAxis=object(), bRepBodies=bodies),
               fusion=NS(FeatureOperations=NS(NewBodyFeatureOperation=0, CutFeatureOperation=1, JoinFeatureOperation=2)),
               plane=Mock(), profile=Mock(), sphere=Mock(), extrude=extrude,
               mirror=mirror, pattern=pattern, combine=combine)
        def finished_mount(native, anchor):
            return extrude(None, None, None, 'finished mount ' + str(len(bodies))).bodies.item(0)
        with patch.object(model, 'mount_make_rear_body', side_effect=finished_mount), \
             patch.object(model, 'mount_make_body_front', side_effect=finished_mount):
            model.build_mounts(n, shell)

    def test_build_uses_root_and_moves_each_part_before_next_build(self):
        self.design.userParameters.add = Mock()
        core = NS(ValueInput=NS(createByString=lambda value: value))
        sys.modules['adsk'].core = core
        events = []
        n = NS(translate=lambda body, *args: events.append(('move', body.name)),
               pattern=Mock(),
               comp=self.root, cm=lambda expression: 4.8)
        self.root.xConstructionAxis = object()
        def pattern(*args):
            source = self.root.bRepBodies.itemByName('Latch')
            copy = self.body('copy', [28, 31.835144, 6])
            copy.preciseBoundingBox.minPoint.x += 4.8
            copy.preciseBoundingBox.maxPoint.x += 4.8
            # Old global-difference selection sees all wrappers as new, including
            # an unrelated body; feature.bodies is the authoritative output.
            self.root.bRepBodies[:] = [self.body(b.name, [28, 31.835144, 6])
                                      for b in self.root.bRepBodies]
            self.root.bRepBodies.extend([copy, self.body('unrelated', [1, 1, 1])])
            return NS(bodies=Collection([source, copy]))
        n.pattern.side_effect = pattern
        def latch(native):
            self.assertIs(native, n)
            events.append(('build', 'Latch'))
            body = self.body('Latch', [28, 31.835144, 6])
            self.root.bRepBodies.append(body)
            return body
        def shell(native, lid):
            self.assertIs(native, n)
            name = 'Lid' if lid else 'Body'
            events.append(('build', name))
            body = self.body(name, [28, 31.835144, 6])
            self.root.bRepBodies.append(body)
            return body
        with patch.dict(sys.modules, {'adsk.core': core}), \
             patch.object(model, 'Native', return_value=n) as ctor, \
             patch.object(model, 'build_latch', side_effect=latch), \
             patch.object(model, 'build_shell', side_effect=shell), \
             patch.object(model, 'build_mounts', side_effect=lambda n, b, lid: events.append(('mount', b.name))), \
             patch.object(model, 'cut_cavity', side_effect=lambda n, b, lid: events.append(('cavity', b.name))):
            model.build(self.design, Mock())
        ctor.assert_called_once_with(self.design, self.root, unittest.mock.ANY)
        self.assertEqual(events, [('build', 'Latch'), ('move', 'Latch'),
                                 ('build', 'Lid'), ('mount', 'Lid'), ('cavity', 'Lid'), ('move', 'Lid'),
                                 ('build', 'Body'), ('mount', 'Body'), ('cavity', 'Body')])
        self.assertEqual(n.pattern.call_args.args[0][0].name, 'Latch')
        self.assertEqual(n.pattern.call_args.args[2], '48 mm')
        self.assertEqual(self.root.bRepBodies[-2].name, 'Latch 2')
        self.assertEqual(self.root.bRepBodies[-1].name, 'unrelated')


if __name__ == '__main__':
    unittest.main()
