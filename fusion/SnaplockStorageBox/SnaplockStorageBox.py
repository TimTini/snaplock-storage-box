import math
import hashlib
import json
import traceback
from datetime import datetime
from pathlib import Path

# All public dimensions are millimetres; Fusion stores centimetres internally.
VERIFY_VARIANTS = True
DEFAULTS = {
    'length': 237.85, 'width': 123.15, 'body_height': 52.0,
    'lid_height': 15.0, 'wall': 3.0, 'body_floor': 2.0, 'lid_floor': 3.0,
    'corner_radius': 12.0, 'body_inner_radius': 8.0,
    'bottom_bevel': 5.0, 'body_inner_bevel': 4.7, 'mount_end': 32.9,
    'pin_radius': 5.0, 'latch_ball_radius': 3.75, 'fit_clearance': 0.0,
    'latch_thickness': 6.0, 'layout_gap': 20.0,
}
DERIVED = {
    'inner_length': 'length - 2 * wall',
    'inner_width': 'width - 2 * wall',
    'outer_bevel_height': 'bottom_bevel * sqrt(3)',
    'body_inner_bevel_top': 'body_floor + body_inner_bevel * sqrt(3)',
    'lid_inner_bevel': 'bottom_bevel - wall + lid_floor / sqrt(3)',
    'lid_inner_bevel_top': 'lid_floor + lid_inner_bevel * sqrt(3)',
    'mount_spacing': 'length - 2 * mount_end',
    'lid_mount_end': 'mount_end + 0.1 mm',
    'lid_layout_y': 'width + layout_gap + 18 mm',
    'latch_layout_y': '2 * width + 2 * layout_gap + 36 mm',
}


def dimensions(p):
    """Validate fit-critical inputs before creating any Fusion document."""
    for name, value in p.items():
        if not isinstance(value, (float, int)) or not math.isfinite(value):
            raise ValueError('Non-finite dimension: ' + name)
        if value <= 0 and name != 'fit_clearance':
            raise ValueError('Dimension must be positive: ' + name)
    if p['fit_clearance'] < 0 or p['fit_clearance'] >= .5:
        raise ValueError('fit_clearance must be in [0, 0.5) mm')
    if p['corner_radius'] <= p['bottom_bevel']:
        raise ValueError('corner_radius must exceed bottom_bevel')
    if p['body_inner_radius'] <= p['body_inner_bevel']:
        raise ValueError('body_inner_radius must exceed body_inner_bevel')
    if not 4.5 < p['pin_radius'] <= 5.5:
        raise ValueError('pin_radius must be in (4.5, 5.5] mm for the pivot envelope')
    if not 3.5 <= p['latch_ball_radius'] <= 4:
        raise ValueError('latch_ball_radius must be in [3.5, 4] mm')
    if not 5 <= p['latch_thickness'] <= 6.5:
        raise ValueError('latch_thickness must be in [5, 6.5] mm for the measured ramp/notch')
    if p['length'] <= 2 * p['mount_end'] + 39:
        raise ValueError('length does not leave space between the mount pairs')
    if p['width'] <= 2 * p['corner_radius'] + 2 * p['wall']:
        raise ValueError('width is too small for the cavity corners')
    lid_bevel = p['bottom_bevel'] - p['wall'] + p['lid_floor'] / math.sqrt(3)
    if lid_bevel <= 0 or lid_bevel >= p['corner_radius'] - p['wall']:
        raise ValueError('lid inner bevel must be positive and smaller than its inside corner radius')
    if p['mount_end'] <= p['corner_radius'] + 19.5:
        raise ValueError('mount_end places a mounting web on a rounded corner')
    if 2 * p['corner_radius'] >= min(p['length'], p['width']):
        raise ValueError('outside corner radius consumes the straight sides')
    if 2 * p['body_inner_radius'] >= min(p['length'], p['width']) - 2 * p['wall']:
        raise ValueError('inside corner radius consumes the cavity')
    # Source uses 60-degree planar bevels with independent wall/floor thickness.
    root3 = math.sqrt(3)
    d = {
        'inner_length': p['length'] - 2 * p['wall'],
        'inner_width': p['width'] - 2 * p['wall'],
        'outer_bevel_height': p['bottom_bevel'] * root3,
        'body_inner_bevel_top': p['body_floor'] + p['body_inner_bevel'] * root3,
        'lid_inner_bevel_top': p['lid_floor'] + (p['bottom_bevel'] - p['wall'] + p['lid_floor'] / root3) * root3,
        'mount_spacing': p['length'] - 2 * p['mount_end'],
        'mount_centres': [p['mount_end'], p['length'] - p['mount_end']],
        'lid_mount_centres': [p['mount_end'] + .1, p['length'] - p['mount_end'] + .1],
    }
    if p['body_height'] <= max(d['body_inner_bevel_top'], d['outer_bevel_height']) + 20:
        raise ValueError('body_height is too small for the mounts and floor bevel')
    if p['lid_height'] <= max(d['lid_inner_bevel_top'], d['outer_bevel_height']) + 3:
        raise ValueError('lid_height is too small for the cavity bevel')
    if p['wall'] >= p['corner_radius'] or p['wall'] >= p['width'] / 2:
        raise ValueError('wall consumes the cavity')
    return d

class Native:
    """Small helpers for dimensioned sketches and native Fusion features."""
    def __init__(self, design, component, progress):
        import adsk.core as core
        import adsk.fusion as fusion
        self.core, self.fusion = core, fusion
        self.design, self.comp, self.progress = design, component, progress
        self.value = core.ValueInput.createByString
        self.point = core.Point3D.create

    def cm(self, expression):
        return self.design.unitsManager.evaluateExpression(expression, 'mm')

    def objects(self, items):
        result = self.core.ObjectCollection.create()
        for item in items:
            result.add(item)
        return result

    def plane(self, base, offset, name):
        # Only literal zero is constant. Do not collapse a parameter/expression
        # whose current value happens to be zero: it must remain associative.
        if offset == '0 mm':
            return base
        inp = self.comp.constructionPlanes.createInput()
        if not inp.setByOffset(base, self.value(offset)):
            raise RuntimeError('Cannot define plane: ' + name)
        result = self.comp.constructionPlanes.add(inp)
        result.name, result.isLightBulbOn = name, False
        return result

    def coordinates(self, sk, base, coords):
        """Map model-plane expressions (X,Y) or (Y,Z) to actual sketch axes."""
        if base == self.comp.xYConstructionPlane:
            axes = ('x', 'y')
        elif base == self.comp.yZConstructionPlane:
            axes = ('y', 'z')
        else:
            raise ValueError('Unsupported profile plane')
        mapped = []
        for direction in (sk.xDirection, sk.yDirection):
            coefficients = [getattr(direction, axis) for axis in axes]
            indices = [i for i, value in enumerate(coefficients) if abs(value) > 1e-8]
            if len(indices) != 1 or abs(abs(coefficients[indices[0]]) - 1) > 1e-8:
                raise RuntimeError('Sketch axes are not aligned with the model plane')
            index = indices[0]
            mapped.append(coords[index] if coefficients[index] > 0 else '-(' + coords[index] + ')')
        return tuple(mapped)

    def require_constrained(self, sketch):
        if sketch.isFullyConstrained:
            return
        free = []
        for label, collection in [('point', sketch.sketchPoints), ('curve', sketch.sketchCurves)]:
            for i in range(collection.count):
                entity = collection.item(i)
                if entity.isFullyConstrained:
                    continue
                row = {'entity': '{}[{}]'.format(label, i), 'type': entity.objectType,
                       'constraints': entity.geometricConstraints.count,
                       'dimensions': entity.sketchDimensions.count}
                if label == 'point':
                    p = entity.geometry
                    row['sketch_coordinates_mm'] = [p.x * 10, p.y * 10, p.z * 10]
                free.append(row)
        report = {'sketch': sketch.name, 'constraints': sketch.geometricConstraints.count,
                  'dimensions': sketch.sketchDimensions.count, 'free_entities': free}
        self.progress('SKETCH_CONSTRAINT_DIAGNOSTIC ' + json.dumps(report))
        raise RuntimeError('Sketch is not fully constrained: ' + sketch.name +
                           '; free entities=' + str(len(free)) + '; see diagnostic in last-run.log')

    def profile(self, base, offset, coords, name, arcs=None):
        """Closed lines/arcs with driven endpoint coordinates and arc radii."""
        plane = self.plane(base, offset, name + ' plane')
        sk = self.comp.sketches.add(plane)
        sk.name = name
        coords = [self.coordinates(sk, base, pair) for pair in coords]
        arcs = {index: (self.coordinates(sk, base, middle), radius)
                for index, (middle, radius) in (arcs or {}).items()}
        datums = []
        for a, b in [((0, -1, 0), (0, 1, 0)), ((-1, 0, 0), (1, 0, 0))]:
            line = sk.sketchCurves.sketchLines.addByTwoPoints(self.point(*a), self.point(*b))
            line.isConstruction = True
            line.isFixed = True
            line.startSketchPoint.isFixed = True
            line.endSketchPoint.isFixed = True
            datums.append(line)
        points = []
        for expressions in coords:
            xy = [self.cm(e) for e in expressions]
            pt = sk.sketchPoints.add(self.point(*xy, 0))
            points.append(pt)
        arcs = arcs or {}
        for i, pt in enumerate(points):
            end = points[(i + 1) % len(points)]
            if i in arcs:
                middle, radius = arcs[i]
                arc = sk.sketchCurves.sketchArcs.addByThreePoints(
                    pt, self.point(self.cm(middle[0]), self.cm(middle[1]), 0), end)
                dim = sk.sketchDimensions.addRadialDimension(arc, self.point(.3, .3, 0))
                dim.parameter.expression = radius
            else:
                sk.sketchCurves.sketchLines.addByTwoPoints(pt, end)
        # Constrain the completed connected profile. Applying all dimensions to
        # isolated points before adding lines can leave curve solver status stale.
        for pt, expressions in zip(points, coords):
            xy = [self.cm(e) for e in expressions]
            for axis, expression in enumerate(expressions):
                if abs(xy[axis]) < 1e-8:
                    method = (sk.geometricConstraints.addVerticalPoints,
                              sk.geometricConstraints.addHorizontalPoints)[axis]
                    method(sk.originPoint, pt)
                else:
                    dim = sk.sketchDimensions.addOffsetDimension(
                        datums[axis], pt, self.point(xy[0] + .3, xy[1] + .3, 0), True)
                    dim.parameter.expression = 'abs(' + expression + ')'
        if sk.profiles.count != 1:
            raise RuntimeError('{}: expected one closed profile, found {}'.format(name, sk.profiles.count))
        self.require_constrained(sk)
        return sk

    def rectangle(self, base, offset, x, y, w, h, name):
        return self.profile(base, offset, [(x, y), ('('+x+') + ('+w+')', y),
            ('('+x+') + ('+w+')', '('+y+') + ('+h+')'),
            (x, '('+y+') + ('+h+')')], name)

    def rounded(self, z, inset, radius, name):
        """Rounded rectangles use eight analytic edges, never mesh facets."""
        a, b, r = '('+inset+')', '('+inset+')', '('+radius+')'
        right, top = 'length - '+a, 'width - '+b
        coords = [(a+' + '+r, b), (right+' - '+r, b),
                  (right, b+' + '+r), (right, top+' - '+r),
                  (right+' - '+r, top), (a+' + '+r, top),
                  (a, top+' - '+r), (a, b+' + '+r)]
        k = r+' / sqrt(2)'
        arcs = {
            1: ((right+' - '+r+' + '+k, b+' + '+r+' - '+k), radius),
            3: ((right+' - '+r+' + '+k, top+' - '+r+' + '+k), radius),
            5: ((a+' + '+r+' - '+k, top+' - '+r+' + '+k), radius),
            7: ((a+' + '+r+' - '+k, b+' + '+r+' - '+k), radius),
        }
        return self.profile(self.comp.xYConstructionPlane, z, coords, name, arcs)

    def feature(self, result, name):
        if result is None:
            raise RuntimeError('Fusion did not create: ' + name)
        result.name = name
        self.progress(self.comp.name + ': ' + name)
        if result.healthState != self.fusion.FeatureHealthStates.HealthyFeatureHealthState:
            raise RuntimeError(name + ': ' + result.errorOrWarningMessage)
        return result

    def extrude(self, sk, distance, operation, name, target=None, negative=False):
        inp = self.comp.features.extrudeFeatures.createInput(sk.profiles.item(0), operation)
        direction = (self.fusion.ExtentDirections.NegativeExtentDirection if negative
                     else self.fusion.ExtentDirections.PositiveExtentDirection)
        inp.setOneSideExtent(self.fusion.DistanceExtentDefinition.create(self.value(distance)), direction)
        if operation in (self.fusion.FeatureOperations.CutFeatureOperation, self.fusion.FeatureOperations.IntersectFeatureOperation):
            inp.participantBodies = [target]
        result = self.feature(self.comp.features.extrudeFeatures.add(inp), name)
        sk.isVisible = False
        return result

    def loft(self, lower, upper, operation, name, target=None):
        return self.section_loft([lower, upper], operation, name, target)

    def section_loft(self, sketches, operation, name, target=None):
        inp = self.comp.features.loftFeatures.createInput(operation)
        for sketch in sketches:
            inp.loftSections.add(sketch.profiles.item(0))
        inp.isSolid = True
        if operation in (self.fusion.FeatureOperations.CutFeatureOperation, self.fusion.FeatureOperations.IntersectFeatureOperation):
            inp.participantBodies = [target]
        result = self.feature(self.comp.features.loftFeatures.add(inp), name)
        for sketch in sketches:
            sketch.isVisible = False
        return result

    def sphere(self, x, y, z, radius, operation, name, target=None):
        # A semicircle revolved around its diameter gives an exact native sphere.
        sk = self.profile(self.comp.xYConstructionPlane, z,
            [('('+x+') - ('+radius+')', y), ('('+x+') + ('+radius+')', y)],
            name + ' semicircle',
            {0: ((x, '('+y+') + ('+radius+')'), radius)})
        diameter = sk.sketchCurves.sketchLines.item(sk.sketchCurves.sketchLines.count - 1)
        inp = self.comp.features.revolveFeatures.createInput(sk.profiles.item(0), diameter, operation)
        inp.setAngleExtent(False, self.value('360 deg'))
        if operation in (self.fusion.FeatureOperations.CutFeatureOperation, self.fusion.FeatureOperations.IntersectFeatureOperation):
            inp.participantBodies = [target]
        result = self.feature(self.comp.features.revolveFeatures.add(inp), name)
        sk.isVisible = False
        return result

    def pattern(self, features, axis, spacing, name):
        inp = self.comp.features.rectangularPatternFeatures.createInput(
            self.objects(features), axis, self.value('2'), self.value(spacing),
            self.fusion.PatternDistanceType.SpacingPatternDistanceType)
        # Fusion also has a second pattern direction. Define it explicitly;
        # otherwise inherited/default quantity can create an unwanted 2D grid.
        inp.quantityTwo = self.value('1')
        return self.feature(self.comp.features.rectangularPatternFeatures.add(inp), name)

    def mirror(self, features, plane, name):
        inp = self.comp.features.mirrorFeatures.createInput(self.objects(features), plane)
        inp.patternComputeOption = self.fusion.PatternComputeOptions.IdenticalPatternCompute
        return self.feature(self.comp.features.mirrorFeatures.add(inp), name)

    def translate(self, body, x, y, z, name):
        inp = self.comp.features.moveFeatures.createInput2(self.objects([body]))
        inp.defineAsTranslateXYZ(self.value(x), self.value(y), self.value(z), False)
        return self.feature(self.comp.features.moveFeatures.add(inp), name)


    def circle(self, base, offset, x, y, radius, name):
        # Use a separate sketch: one circle is a single, unambiguous profile.
        plane = self.plane(base, offset, name + ' plane')
        sk = self.comp.sketches.add(plane)
        sk.name = name
        x, y = self.coordinates(sk, base, (x, y))
        center = self.point(self.cm(x), self.cm(y), 0)
        curve = sk.sketchCurves.sketchCircles.addByCenterRadius(center, self.cm(radius))
        for axis, expr in enumerate((x, y)):
            direction = (self.fusion.DimensionOrientations.HorizontalDimensionOrientation,
                         self.fusion.DimensionOrientations.VerticalDimensionOrientation)[axis]
            if abs(self.cm(expr)) < 1e-8:
                method = (sk.geometricConstraints.addVerticalPoints,
                          sk.geometricConstraints.addHorizontalPoints)[axis]
                method(sk.originPoint, curve.centerSketchPoint)
            else:
                dim = sk.sketchDimensions.addDistanceDimension(
                    sk.originPoint, curve.centerSketchPoint, direction, self.point(center.x+.5, center.y+.5, 0))
                dim.parameter.expression = 'abs(' + expr + ')'
        dim = sk.sketchDimensions.addRadialDimension(curve, self.point(center.x+.5, center.y+.5, 0))
        dim.parameter.expression = radius
        self.require_constrained(sk)
        return sk

    def fillet(self, edges, radius, name):
        inp = self.comp.features.filletFeatures.createInput()
        inp.edgeSetInputs.addConstantRadiusEdgeSet(self.objects(edges), self.value(radius), False)
        return self.feature(self.comp.features.filletFeatures.add(inp), name)

    def combine(self, target, tools, operation, name):
        inp = self.comp.features.combineFeatures.createInput(target, self.objects(tools))
        inp.operation = operation
        inp.isKeepToolBodies = False
        return self.feature(self.comp.features.combineFeatures.add(inp), name)


def build_shell(n, lid=False):
    op = n.fusion.FeatureOperations
    prefix = 'Lid' if lid else 'Body'
    height = 'lid_height' if lid else 'body_height'
    lower = n.rounded('0 mm', 'bottom_bevel', 'corner_radius - bottom_bevel', prefix + ' outside foot')
    upper = n.rounded('outer_bevel_height', '0 mm', 'corner_radius', prefix + ' outside wall')
    body = n.loft(lower, upper, op.NewBodyFeatureOperation, 'Outside 60 degree bevel').bodies.item(0)
    n.extrude(upper, height+' - outer_bevel_height', op.JoinFeatureOperation, 'Straight walls')
    body.name = prefix
    return body


def cut_cavity(n, body, lid=False):
    # Cut after mount union, matching SCAD and keeping the inside wall clear.
    op = n.fusion.FeatureOperations
    prefix = 'Lid' if lid else 'Body'
    height = 'lid_height' if lid else 'body_height'
    floor = 'lid_floor' if lid else 'body_floor'
    bevel = 'lid_inner_bevel' if lid else 'body_inner_bevel'
    bevel_top = 'lid_inner_bevel_top' if lid else 'body_inner_bevel_top'
    inner_radius = 'corner_radius - wall' if lid else 'body_inner_radius'
    lower = n.rounded(floor, 'wall + '+bevel, inner_radius+' - '+bevel, prefix + ' inside floor')
    upper = n.rounded(bevel_top, 'wall', inner_radius, prefix + ' inside wall')
    n.loft(lower, upper, op.CutFeatureOperation, 'Inside floor bevel', body)
    n.extrude(upper, height+' - '+bevel_top+' + 6 mm', op.CutFeatureOperation, 'Open cavity', body)


def mount_offset(anchor, delta):
    return '(' + anchor + ') + (' + delta + ')'


def mount_plan_tool(n, offset, points, height, name):
    sk = n.profile(n.comp.xYConstructionPlane, offset, points, name + ' profile')
    return n.extrude(sk, height, n.fusion.FeatureOperations.NewBodyFeatureOperation,
                     name).bodies.item(0)


def mount_yz_web(n, anchor, start, span, points, name, arcs=None):
    sk = n.profile(n.comp.yZConstructionPlane, mount_offset(anchor, start), points, name + ' profile', arcs)
    return n.extrude(sk, span, n.fusion.FeatureOperations.NewBodyFeatureOperation,
                     name).bodies.item(0)


def mount_intersect(n, target, tools, name):
    n.combine(target, tools, n.fusion.FeatureOperations.IntersectFeatureOperation, name)
    return target


def mount_make_rear_body(n, anchor):
    op = n.fusion.FeatureOperations
    rear = mount_yz_web(n, anchor, '-22 mm', '11 mm', [
        ('1 mm', 'body_height - 15 mm'), ('0 mm', 'body_height - 15 mm'),
        ('-8.3045298 mm', 'body_height - 2.3297678 mm'),
        ('-0.5 mm', 'body_height'), ('1 mm', 'body_height')],
        'Rear hinge web', {2: (('-4.75 mm', 'body_height + 4.25 mm'), '4.2500000 mm')})
    clip = mount_plan_tool(n, '0 mm', [
        (mount_offset(anchor, '-21.2757 mm'), '1 mm'),
        (mount_offset(anchor, '-20.2757 mm'), '0 mm'),
        (mount_offset(anchor, '-18.7035 mm'), '-1.5723 mm'),
        (mount_offset(anchor, '-19.2757 mm + 10 mm * tan(20 deg)'), '-10 mm'),
        (mount_offset(anchor, '-11 mm'), '-10 mm'),
        (mount_offset(anchor, '-11 mm'), '1 mm')],
        'body_height + 5 mm', 'Rear hinge footprint')
    mount_intersect(n, rear, [clip], 'Clip rear hinge web')
    n.sphere(mount_offset(anchor, '-7 mm'), '-4.75 mm', 'body_height',
             'pin_radius + fit_clearance', op.CutFeatureOperation, 'Rear spherical socket', rear)
    return rear


def mount_make_body_front(n, anchor):
    op = n.fusion.FeatureOperations
    web = mount_yz_web(n, anchor, '-22 mm', '13.1 mm', [
        ('width - 1 mm', 'body_height - 19 mm'),
        ('width', 'body_height - 19 mm'),
        ('width + 2.8113 mm', 'body_height - 15.7393 mm'),
        ('width + 5.4796 mm', 'body_height - 12.3605 mm'),
        ('width + 8 mm', 'body_height - 8.8701 mm'),
        ('width + 8 mm', 'body_height - 1 mm'), ('width + 7 mm', 'body_height'),
        ('width - 1 mm', 'body_height')],
        'Front catch web', {5: (('width + 7 mm + 1 mm / sqrt(2)',
                                 'body_height - 1 mm + 1 mm / sqrt(2)'), '1 mm')})
    footprint = mount_plan_tool(n, '0 mm', [
        (mount_offset(anchor, '-21.3 mm'), 'width - 1 mm'),
        (mount_offset(anchor, '-20.9 mm'), 'width'),
        (mount_offset(anchor, '-17.75 mm'), 'width + 8 mm'),
        (mount_offset(anchor, '-8.9 mm'), 'width + 8 mm'),
        (mount_offset(anchor, '-8.9 mm'), 'width - 1 mm')],
        'body_height + 5 mm', 'Front catch footprint')
    mount_intersect(n, web, [footprint], 'Clip front catch footprint')

    pad = n.rectangle(n.comp.xYConstructionPlane, '0 mm', mount_offset(anchor, '-22 mm'),
                      'width - 2 mm', '9.25 mm', '12 mm', 'Front catch pad profile')
    pad_body = n.extrude(pad, 'body_height + 5 mm', op.NewBodyFeatureOperation,
                         'Front catch pad').bodies.item(0)
    lower = n.circle(n.comp.yZConstructionPlane, mount_offset(anchor, '-12.75 mm'),
                     'width + 3 mm', 'body_height + 9 mm',
                     '9.486833 mm + 3.734 mm * tan(50 deg)', 'Front lip base')
    upper = n.circle(n.comp.yZConstructionPlane, mount_offset(anchor, '-9.016 mm'),
                     'width + 3 mm', 'body_height + 9 mm', '9.486833 mm', 'Front lip tip')
    lip = n.loft(lower, upper, op.NewBodyFeatureOperation, 'Front annular lip cone').bodies.item(0)
    bore = n.circle(n.comp.yZConstructionPlane, mount_offset(anchor, '-12.75 mm'),
                    'width + 3 mm', 'body_height + 9 mm', '9.5 mm', 'Front lip bore profile')
    n.extrude(bore, '3.734 mm', op.CutFeatureOperation, 'Front lip bore', lip)
    n.combine(pad_body, [lip], op.JoinFeatureOperation, 'Join front pad and lip')
    mount_intersect(n, web, [pad_body], 'Trim front catch to pad and lip')

    # SCAD's vertical bore has two one-millimetre conical chamfers and a 4.5 mm barrel.
    x, y = mount_offset(anchor, '-8.75 mm'), 'width + 3 mm'
    bottom = n.circle(n.comp.xYConstructionPlane, 'body_height - 11.5 mm', x, y,
                      '4 mm', 'Front pocket lower chamfer start')
    bottom2 = n.circle(n.comp.xYConstructionPlane, 'body_height - 10.5 mm', x, y,
                       '5 mm', 'Front pocket lower chamfer end')
    top1 = n.circle(n.comp.xYConstructionPlane, 'body_height - 6 mm', x, y,
                    '5 mm', 'Front pocket upper chamfer start')
    top2 = n.circle(n.comp.xYConstructionPlane, 'body_height - 5 mm', x, y,
                    '4 mm', 'Front pocket upper chamfer end')
    lower_tool = n.loft(bottom, bottom2, op.NewBodyFeatureOperation,
                         'Front pocket lower chamfer').bodies.item(0)
    barrel_sk = n.circle(n.comp.xYConstructionPlane, 'body_height - 10.5 mm', x, y,
                         '5 mm', 'Front pocket barrel profile')
    barrel_tool = n.extrude(barrel_sk, '4.5 mm', op.NewBodyFeatureOperation,
                            'Front pocket barrel').bodies.item(0)
    upper_tool = n.loft(top1, top2, op.NewBodyFeatureOperation,
                        'Front pocket upper chamfer').bodies.item(0)
    n.combine(web, [lower_tool, barrel_tool, upper_tool], op.CutFeatureOperation,
              'Cut chamfered vertical pocket')
    return web


def mount_make_lid_rear(n, anchor):
    op = n.fusion.FeatureOperations
    rear = mount_yz_web(n, anchor, '-21 mm', '12 mm', [
        ('5 mm', '0 mm'), ('-5.1423 mm', '0 mm'),
        ('-8 mm', '6.1284 mm'), ('-8 mm', 'lid_height - 0.9377 mm'),
        ('0 mm', 'lid_height'), ('1 mm', 'lid_height'), ('5 mm', '8.660254 mm')],
        'Lid latch web', {
            1: (('-7.5175 mm', '3.3922 mm'), '8.000404938210 mm'),
            3: (('-3 mm', 'lid_height + 0.486833 mm'), '9.486985130525 mm')})
    footprint = mount_plan_tool(n, '0 mm', [
        (mount_offset(anchor, '-21 mm'), '5 mm'),
        (mount_offset(anchor, '-21 mm'), '0 mm'),
        (mount_offset(anchor, '-17.75 mm'), '-8 mm'),
        (mount_offset(anchor, '-9 mm'), '-8 mm'),
        (mount_offset(anchor, '-9 mm'), '5 mm')], 'lid_height + 1 mm', 'Lid latch footprint')
    mount_intersect(n, rear, [footprint], 'Clip lid latch footprint')

    pad = n.rectangle(n.comp.xYConstructionPlane, '0 mm', mount_offset(anchor, '-22 mm'),
                      '-9 mm', '9.25 mm', '15 mm', 'Lid latch pad profile')
    pad_body = n.extrude(pad, 'lid_height', op.NewBodyFeatureOperation,
                         'Lid latch pad').bodies.item(0)
    outer = n.circle(n.comp.yZConstructionPlane, mount_offset(anchor, '-12.75 mm'),
                     '-3 mm', '6 mm', '9.5 mm', 'Lid lip outer profile')
    ring = n.extrude(outer, '3.734 mm', op.NewBodyFeatureOperation,
                     'Lid annular lip cylinder').bodies.item(0)
    inner_start = n.circle(n.comp.yZConstructionPlane, mount_offset(anchor, '-12.751 mm'),
        '-3 mm', '6 mm', '9.486833 mm - 3.734 mm * tan(50 deg) - 0.001 mm * tan(50 deg)',
        'Lid lip taper start')
    inner_end = n.circle(n.comp.yZConstructionPlane, mount_offset(anchor, '-9.015 mm'),
        '-3 mm', '6 mm', '9.486833 mm + 0.001 mm * tan(50 deg)', 'Lid lip taper end')
    inner = n.loft(inner_start, inner_end, op.NewBodyFeatureOperation,
                   'Lid annular lip taper tool').bodies.item(0)
    n.combine(ring, [inner], op.CutFeatureOperation, 'Cut tapered lid lip opening')
    clip = n.rectangle(n.comp.xYConstructionPlane, '6 mm', mount_offset(anchor, '-13 mm'),
                       '-9 mm', '5 mm', '15 mm', 'Lid lip clip profile')
    clip_body = n.extrude(clip, 'lid_height + 5 mm', op.NewBodyFeatureOperation,
                          'Lid lip clip').bodies.item(0)
    mount_intersect(n, ring, [clip_body], 'Clip lid lip')
    n.combine(pad_body, [ring], op.JoinFeatureOperation, 'Join lid latch pad and lip')
    mount_intersect(n, rear, [pad_body], 'Trim lid latch to pad and lip')
    n.sphere(mount_offset(anchor, '-10.5 mm'), '-3 mm', '6 mm',
             'latch_ball_radius + fit_clearance', op.CutFeatureOperation,
             'Lid spherical socket', rear)
    return rear


def mount_make_lid_front(n, anchor):
    op = n.fusion.FeatureOperations
    web = mount_yz_web(n, anchor, '-10.75 mm', '10 mm', [
        ('width - 5 mm', '0 mm'), ('width - 1.1 mm', '0 mm'),
        ('width + 0.5968 mm', '1.0901 mm'), ('width + 2.072 mm', '2.3838 mm'),
        ('width + 3.3657 mm', '3.859 mm'), ('width + 4.4558 mm', '5.4904 mm'),
        ('width + 8.6471 mm', 'lid_height - 2.25 mm'),
        ('width + 0.25 mm', 'lid_height'), ('width - 1 mm', 'lid_height'),
        ('width - 5 mm', '8.660254 mm')],
        'Lid pivot web', {
            6: (('width + 4.75 mm', 'lid_height + 4.5 mm'), '4.5 mm')})
    footprint = mount_plan_tool(n, '0 mm', [
        (mount_offset(anchor, '-10.75 mm'), 'width - 5 mm'),
        (mount_offset(anchor, '-2.3833 mm'), 'width - 5 mm'),
        (mount_offset(anchor, '-2.3833 mm'), 'width'),
        (mount_offset(anchor, '-2.3833 mm - 10 mm * tan(20 deg)'), 'width + 10 mm'),
        (mount_offset(anchor, '-10.75 mm'), 'width + 10 mm')],
        'lid_height + 5 mm', 'Lid pivot footprint')
    mount_intersect(n, web, [footprint], 'Clip lid pivot footprint')

    cap = n.sphere(mount_offset(anchor, '-7 mm'), 'width + 4.75 mm', 'lid_height',
                   'pin_radius', op.NewBodyFeatureOperation, 'Lid pivot sphere').bodies.item(0)
    envelope = n.circle(n.comp.yZConstructionPlane, mount_offset(anchor, '-15 mm'),
                        'width + 4.75 mm', 'lid_height', '4.5 mm', 'Pivot envelope profile')
    envelope_body = n.extrude(envelope, '30 mm', op.NewBodyFeatureOperation,
                              'Pivot envelope cylinder').bodies.item(0)
    mount_intersect(n, cap, [envelope_body], 'Limit pivot sphere radially')
    box = n.rectangle(n.comp.xYConstructionPlane, 'lid_height - 5 mm',
                      mount_offset(anchor, '-13 mm'), 'width - 1 mm',
                      '2.251 mm', '11 mm', 'Pivot cap clipping box profile')
    box_body = n.extrude(box, '10 mm', op.NewBodyFeatureOperation,
                         'Pivot cap clipping box').bodies.item(0)
    mount_intersect(n, cap, [box_body], 'Clip pivot sphere cap')
    n.combine(web, [cap], op.JoinFeatureOperation, 'Join clipped pivot cap')
    return web


def build_mounts(n, body, lid=False):
    """Create SCAD-faithful mount solids, then mirror and pattern one site."""
    op = n.fusion.FeatureOperations
    existing_names = {b.name for b in n.comp.bRepBodies}
    anchor = 'lid_mount_end' if lid else 'mount_end'
    mid = n.plane(n.comp.yZConstructionPlane, anchor, 'First site symmetry')
    if lid:
        tools = [mount_make_lid_rear(n, anchor), mount_make_lid_front(n, anchor)]
    else:
        tools = [mount_make_rear_body(n, anchor), mount_make_body_front(n, anchor)]
    n.mirror(tools, mid, 'Mirror first site ends')
    first_site = [b for b in n.comp.bRepBodies if b.name not in existing_names]
    n.pattern(first_site, n.comp.xConstructionAxis, 'mount_spacing', 'Second mounting site')
    n.combine(body, [b for b in n.comp.bRepBodies if b.name not in existing_names],
              op.JoinFeatureOperation, 'Join all mounting webs')


def latch_sections(fraction):
    """Expression-driven sections of the SCAD's measured R5 thickness relief."""
    d = '(5 mm - sqrt((5 mm)^2 - (latch_thickness * ({:.12g} - 0.5))^2))'.format(fraction)
    c = '(2.847 mm - 0.2976 * '+d+')'
    shoulder = '(1.5 mm + 1.35 * '+d+')'
    tip = '(0.5 mm + '+d+')'
    tooth = [(shoulder, '17.0724 mm'), (tip, '18.0724 mm'),
             (tip, '22.0724 mm'), (shoulder, '23.0724 mm'),
             ('3.5 mm', '23.0724 mm'), ('3.5 mm', '17.0724 mm')]
    slot = [('-2 mm', '7.9971 mm - '+d), ('1.5 mm', '7.9971 mm - '+d),
            ('5.234 mm', '12.4458 mm - 0.488 * '+d),
            (c+' - 0.383 mm', '15.751 mm'), (c, '16.5724 mm'),
            ('4.5 mm', '16.5724 mm'), ('5 mm', '17.0724 mm'),
            ('5 mm', '26.0724 mm'), ('4 mm', '26.0724 mm'),
            ('4 mm', '17.5724 mm'), ('3.5 mm', '17.0724 mm'),
            (shoulder, '17.0724 mm'), (tip, '18.0724 mm'), ('-2 mm', '18.0724 mm')]
    # First source arc is specified by three rounded survey points; its exact
    # circumradius avoids constraining those fixed points to a rounded R0.5.
    arcs = {3: ((c+' - 0.4699 mm', '16.2434 mm'), '0.499953592932 mm'),
            5: (('4.5 mm + 0.5 mm / sqrt(2)', '17.0724 mm - 0.5 mm / sqrt(2)'), '.5 mm'),
            7: (('4.5 mm', '26.5724 mm'), '.5 mm'),
            9: (('3.5 mm + 0.5 mm / sqrt(2)', '17.5724 mm - 0.5 mm / sqrt(2)'), '.5 mm')}
    return tooth, slot, arcs


def build_latch(n):
    op = n.fusion.FeatureOperations
    xy, yz = n.comp.xYConstructionPlane, n.comp.yZConstructionPlane
    mid = n.plane(yz, '14 mm', 'Latch symmetry')
    base = n.rectangle(xy, '0 mm', '1.5 mm', '0 mm', '25 mm', '32.9 mm', 'Latch plate')
    body = n.extrude(base, 'latch_thickness', op.NewBodyFeatureOperation, 'Latch blank').bodies.item(0)
    body.name = 'Latch'
    teeth, slots = [], []
    for i in range(25):
        fraction = i / 24
        tooth_coords, slot_coords, arcs = latch_sections(fraction)
        z = 'latch_thickness * {:.12g}'.format(fraction)
        teeth.append(n.profile(xy, z, tooth_coords, 'Catch section {:02d}'.format(i)))
        slots.append(n.profile(xy, z, slot_coords, 'Relief section {:02d}'.format(i), arcs))
    tooth = n.section_loft(teeth, op.JoinFeatureOperation, 'Catch tooth thickness relief')
    n.mirror([tooth], mid, 'Mirror catch tooth')
    ball = n.sphere('3.75 mm', '3 mm', 'latch_thickness / 2', 'latch_ball_radius',
                    op.JoinFeatureOperation, 'Latch pivot sphere')
    n.mirror([ball], mid, 'Mirror pivot sphere')
    # Trim native spheres to the measured print-flat top, bottom and front faces.
    for z, negative, name in [('latch_thickness', False, 'Flat sphere tops'), ('0 mm', True, 'Flat sphere bottoms')]:
        sk = n.rectangle(xy, z, '-2 mm', '-2 mm', '32 mm', '36 mm', name + ' trim')
        n.extrude(sk, 'latch_ball_radius', op.CutFeatureOperation, name, body, negative)
    front_y = '5 mm - sqrt((5 mm)^2 - (latch_thickness / 2)^2)'
    sk = n.profile(yz, '-2 mm', [('-2 mm', '0 mm'), (front_y, '0 mm'),
        (front_y, 'latch_thickness'), ('-2 mm', 'latch_thickness')],
        'Rounded pivot front trim', {1: (('0 mm', 'latch_thickness / 2'), '5 mm')})
    n.extrude(sk, '32 mm', op.CutFeatureOperation, 'R5 pivot front relief', body)
    # Curved notch = cylinder with R2 end fillets (toroidal corner bands).
    sk = n.circle(yz, '6.5 mm', '3 mm', 'latch_thickness / 2', '5 mm', 'Notch tool circle')
    tool = n.extrude(sk, '15 mm', op.NewBodyFeatureOperation, 'Notch cylinder tool').bodies.item(0)
    edges = [e for e in tool.edges if n.core.Circle3D.cast(e.geometry)]
    if len(edges) != 2:
        raise RuntimeError('Notch tool must have exactly two circular end edges')
    n.fillet(edges, '2 mm', 'Notch tool end fillets')
    n.combine(body, [tool], op.CutFeatureOperation, 'Rounded pivot notch')
    # Slot profiles reach X=-2. Mirror of a loft Cut can join that overhang on the
    # far side and grow Latch X from 28 to 30. Cut with mirrored tool bodies instead.
    tool = n.section_loft(slots, op.NewBodyFeatureOperation, 'Spring relief tool').bodies.item(0)
    n.mirror([tool], mid, 'Mirror spring relief tool')
    tools = [b for b in n.comp.bRepBodies if b.name != 'Latch']
    if len(tools) != 2:
        raise RuntimeError('Spring relief tools: expected 2, found ' + str(len(tools)))
    n.combine(body, tools, op.CutFeatureOperation, 'Spring relief cuts')
    # Y+Z=32.9 is a measured plane, not a guessed radius/chamfer.
    sk = n.profile(yz, '-2 mm', [('26.9 mm','latch_thickness'),
        ('31.835144 mm','latch_thickness - 4.935139 mm'),
        ('31.743874 mm','0 mm'),('35 mm','0 mm'),('35 mm','latch_thickness')], 'Latch opening ramp trim')
    n.extrude(sk, '32 mm', op.CutFeatureOperation, 'Opening ramp', body)
    return body


def build(design, progress):
    import adsk.core as core
    dimensions(DEFAULTS)
    params = design.userParameters
    for name, number in DEFAULTS.items():
        params.add(name, core.ValueInput.createByString('{} mm'.format(number)), 'mm',
                   'Snaplock: measured source dimension; see README for fit limits.')
    for name, expr in DERIVED.items():
        params.add(name, core.ValueInput.createByString(expr), 'mm', 'Derived: keep the expression.')
    root = design.rootComponent
    n = Native(design, root, progress)
    # Move each completed part away before constructing the next at the origin.
    # Native Join features then cannot accidentally join a previous part.
    latch = build_latch(n)
    n.translate(latch, '0 mm', 'latch_layout_y', '0 mm', 'Print layout latch')
    for name, lid in [('Lid', True), ('Body', False)]:
        body = build_shell(n, lid)
        body.name = name
        build_mounts(n, body, lid)
        cut_cavity(n, body, lid)
        if lid:
            n.translate(body, '0 mm', 'lid_layout_y', '0 mm', 'Print layout lid')
    # Resolve the current seed after all other features have recomputed.
    latch = root.bRepBodies.itemByName('Latch')
    if latch is None:
        raise RuntimeError('Missing Latch body before pattern')
    expected_x = latch.preciseBoundingBox.minPoint.x + n.cm('48 mm')
    progress('Before latch pattern: ' + str([b.name for b in root.bRepBodies]))
    pattern = n.pattern([latch], root.xConstructionAxis, '48 mm', 'Second latch body')
    progress('Latch pattern output bodies: ' + str([b.name for b in pattern.bodies]))
    # Feature.bodies can include the seed as well as the new body. Select the
    # translated output geometrically, without comparing stale body wrappers.
    copies = [b for b in pattern.bodies if abs(b.preciseBoundingBox.minPoint.x - expected_x) < 1e-6]
    if len(copies) != 1:
        raise RuntimeError('Latch body pattern: expected one new body, found ' + str(len(copies)))
    copies[0].name = 'Latch 2'


def check_model(design):
    import adsk.fusion as fusion
    p = {name: design.userParameters.itemByName(name).value * 10 for name in DEFAULTS}
    dimensions(p)
    if not design.computeAll():
        raise RuntimeError('Fusion computeAll failed')
    root = design.rootComponent
    if root.allOccurrences.count != 0:
        raise RuntimeError('Expected only the root component, without child occurrences')
    names = {'Body', 'Lid', 'Latch', 'Latch 2'}
    if root.bRepBodies.count != 4 or {b.name for b in root.bRepBodies} != names:
        raise RuntimeError('Expected four named solid bodies: Body, Lid, Latch, Latch 2; found ' +
                           str([b.name for b in root.bRepBodies]))
    for i in range(design.timeline.count):
        entity = design.timeline.item(i).entity
        if isinstance(entity, fusion.Feature) and entity.healthState != fusion.FeatureHealthStates.HealthyFeatureHealthState:
            raise RuntimeError(entity.name + ': ' + entity.errorOrWarningMessage)
    report = []
    for sk in root.sketches:
        if not sk.isFullyConstrained:
            raise RuntimeError('Unconstrained sketch: ' + sk.name)
    for b in root.bRepBodies:
        if not b.isSolid:
            raise RuntimeError(b.name + ': expected a solid body')
        if b.volume <= 0:
            raise RuntimeError(b.name + ': non-positive volume')
        box = b.preciseBoundingBox
        extents = [(getattr(box.maxPoint, a) - getattr(box.minPoint, a)) * 10 for a in 'xyz']
        expected = {
            'Body': [p['length'], p['width'] + 17, p['body_height'] + 4.25],
            'Lid': [p['length'], p['width'] + 17.25, p['lid_height'] + 4.5],
            'Latch': [20.5 + 2 * p['latch_ball_radius'], 31.835144, p['latch_thickness']],
            'Latch 2': [20.5 + 2 * p['latch_ball_radius'], 31.835144, p['latch_thickness']],
        }[b.name]
        if any(abs(actual - wanted) > .02 for actual, wanted in zip(extents, expected)):
            raise RuntimeError(b.name + ': unexpected bounds ' + str(extents) + '; expected ' + str(expected))
        report.append('{}: bounds_mm={}, volume_mm3={:.3f}'.format(b.name, extents, b.volume * 1000))
    return report


def verify_variants(design, progress):
    params = design.userParameters
    saved = {name: params.itemByName(name).expression for name in DEFAULTS}
    try:
        for variant in [{'length': '280 mm', 'width': '155 mm', 'body_height': '70 mm'},
                        {'fit_clearance': '0.2 mm'}]:
            for name, expr in variant.items():
                params.itemByName(name).expression = expr
            progress('Verify parameter variant: ' + str(variant))
            check_model(design)
            for name, expr in saved.items():
                params.itemByName(name).expression = expr
            check_model(design)
    finally:
        for name, expr in saved.items():
            params.itemByName(name).expression = expr
        check_model(design)


def export_meshes(design, fusion, output):
    """Export the actual native solids in mm; record hashes for offline audit."""
    output.mkdir(parents=True, exist_ok=True)
    manifest = {'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'units': 'mm', 'parts': {}}
    for body in design.rootComponent.bRepBodies:
        path = output / (body.name.lower().replace(' ', '-') + '.stl')
        options = design.exportManager.createSTLExportOptions(body, str(path))
        options.unitType = fusion.DistanceUnits.MillimeterDistanceUnits
        options.meshRefinement = fusion.MeshRefinementSettings.MeshRefinementHigh
        options.surfaceDeviation = .0005  # API cm = 0.005 mm.
        options.normalDeviation = math.radians(.5)
        options.maximumEdgeLength = .1  # API cm = 1 mm.
        options.isBinaryFormat = True
        options.sendToPrintUtility = False
        if not design.exportManager.execute(options) or not path.is_file():
            raise RuntimeError('STL export failed: ' + body.name)
        manifest['parts'][body.name] = {'file': path.name,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
    if set(manifest['parts']) != {'Body', 'Lid', 'Latch', 'Latch 2'}:
        raise RuntimeError('STL export requires exactly four named bodies')
    manifest['mesh_settings'] = {'surface_deviation_mm': .005, 'normal_deviation_degrees': .5,
                                 'maximum_edge_length_mm': 1}
    path = output / 'manifest.json'
    path.write_text(json.dumps(manifest, indent=2), encoding='utf8')
    return path


def run(context):
    import adsk.core as core
    import adsk.fusion as fusion
    import adsk
    app = core.Application.get()
    ui = app.userInterface
    log_path = Path(__file__).with_name('last-run.log')
    stage = 'Validate dimensions'
    lines = ['SnaplockStorageBox — native Fusion run',
             'Script SHA256: ' + __import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest()]
    dialog = ui.createProgressDialog()
    def progress(message):
        nonlocal stage
        stage = message
        lines.append(message)
        log_path.write_text('\n'.join(lines), encoding='utf8')
        dialog.message = message
        dialog.progressValue += 1
        adsk.doEvents()
    try:
        dimensions(DEFAULTS)
        document = app.documents.add(core.DocumentTypes.FusionDesignDocumentType)
        document.name = 'Snaplock Storage Box — native feature reconstruction'
        design = fusion.Design.cast(app.activeProduct)
        if design is None:
            raise RuntimeError('New document is not a Fusion design')
        design.designType = fusion.DesignTypes.ParametricDesignType
        design.unitsManager.distanceDisplayUnits = fusion.DistanceUnits.MillimeterDistanceUnits
        dialog.isCancelButtonShown = False
        dialog.show('Snaplock Storage Box', 'Build native features', 0, 300, 0)
        progress('Build native bodies')
        build(design, progress)
        progress('Verify four root bodies and timeline')
        lines.extend(check_model(design))
        if VERIFY_VARIANTS:
            verify_variants(design, progress)
        progress('Export native body STL files for comparison')
        output = Path(__file__).parent / 'exports' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        manifest = export_meshes(design, fusion, output)
        lines.append('Native STL manifest: ' + str(manifest))
        lines.append('NATIVE_BUILD_AND_RECOMPUTE_OK; physical snap fit not tested.')
        log_path.write_text('\n'.join(lines), encoding='utf8')
        app.activeViewport.fit()
        ui.messageBox('Đã tạo thân, nắp và 2 khóa bằng native features.\n'
                      'Chỉnh Modify > Change Parameters.\n'
                      'STL đối chiếu: ' + str(output) + '\nLog: ' + str(log_path))
    except Exception:
        lines.append('FAILED at ' + stage + '\n' + traceback.format_exc())
        log_path.write_text('\n'.join(lines), encoding='utf8')
        ui.messageBox('Lỗi tại ' + stage + '\n' + traceback.format_exc() + '\nLog: ' + str(log_path))
    finally:
        dialog.hide()
