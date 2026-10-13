"""Run directly as a Fusion add-in; each run creates three new documents."""

import hashlib
import json
import math
from pathlib import Path
import traceback

import adsk.core
import adsk.fusion


CASES = ('A_separate_planes', 'B_shared_plane', 'C_extrude_offset')
STATES = (
    ('initial', {'demo_z': '10 mm', 'demo_diameter': '10 mm', 'demo_height': '4 mm'}),
    ('variant', {'demo_z': '18 mm', 'demo_diameter': '12 mm', 'demo_height': '6 mm'}),
    ('restored', {'demo_z': '10 mm', 'demo_diameter': '10 mm', 'demo_height': '4 mm'}),
)
REPORT = Path(__file__).parent / 'results' / 'last-run.json'


def value(expression):
    return adsk.core.ValueInput.createByString(expression)


def offset_plane(component, name):
    plane_input = component.constructionPlanes.createInput()
    if not plane_input.setByOffset(component.xYConstructionPlane, value('demo_z')):
        raise RuntimeError('Offset plane definition failed: ' + name)
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    plane.isLightBulbOn = False
    return plane


def build_case(app, case):
    document = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    document.name = 'PlaneSketchTest_' + case
    design = adsk.fusion.Design.cast(document.products.itemByProductType('DesignProductType'))
    if not design:
        raise RuntimeError('New document has no Fusion design')
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    for name, expression in STATES[0][1].items():
        design.userParameters.add(name, value(expression), 'mm', 'Plane/sketch comparison')
    component = design.rootComponent
    shared = offset_plane(component, 'Shared Z plane') if case == CASES[1] else None
    for index in range(3):
        if case == CASES[0]:
            plane = offset_plane(component, 'Separate Z plane {}'.format(index + 1))
        elif case == CASES[1]:
            plane = shared
        else:
            plane = component.xYConstructionPlane
        sketch = component.sketches.add(plane)
        sketch.name = 'Circle {}'.format(index + 1)
        # Fusion internal length unit is cm; centres are fixed demo locations.
        x = 1.5 + index * 2.5
        circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(x, 0, 0), 0.5)
        circle.centerSketchPoint.isFixed = True
        dimension = sketch.sketchDimensions.addDiameterDimension(
            circle, adsk.core.Point3D.create(x + 0.7, 0.7, 0))
        dimension.parameter.expression = 'demo_diameter'
        if sketch.profiles.count != 1:
            raise RuntimeError('Expected one circle profile: ' + sketch.name)
        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(
            sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        if case == CASES[2]:
            extrude_input.startExtent = adsk.fusion.OffsetStartDefinition.create(value('demo_z'))
        extent = adsk.fusion.DistanceExtentDefinition.create(value('demo_height'))
        if not extrude_input.setOneSideExtent(
                extent, adsk.fusion.ExtentDirections.PositiveExtentDirection):
            raise RuntimeError('Extrude extent definition failed')
        extrude = extrudes.add(extrude_input)
        extrude.name = 'Cylinder {}'.format(index + 1)
        extrude.bodies.item(0).name = extrude.name
        sketch.isLightBulbOn = False
    return document, design


def check_case(design, case):
    if not design.computeAll():
        raise RuntimeError(case + ': computeAll failed')
    component = design.rootComponent
    expected_planes = {CASES[0]: 3, CASES[1]: 1, CASES[2]: 0}[case]
    counts = {
        'planes': component.constructionPlanes.count,
        'sketches': component.sketches.count,
        'extrudes': component.features.extrudeFeatures.count,
        'bodies': component.bRepBodies.count,
        'timeline': design.timeline.count,
    }
    expected = {'planes': expected_planes, 'sketches': 3, 'extrudes': 3,
                'bodies': 3, 'timeline': expected_planes + 6}
    if counts != expected:
        raise RuntimeError('{}: counts {} expected {}'.format(case, counts, expected))
    for index in range(design.timeline.count):
        item = design.timeline.item(index)
        if item.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
            raise RuntimeError('{}: timeline item {}: {}'.format(
                case, index, item.errorOrWarningMessage))
    for sketch in component.sketches:
        if not sketch.isFullyConstrained:
            raise RuntimeError(case + ': sketch is underconstrained: ' + sketch.name)
    parameters = design.userParameters
    z = parameters.itemByName('demo_z').value
    radius = parameters.itemByName('demo_diameter').value / 2
    height = parameters.itemByName('demo_height').value
    bodies = []
    for index in range(3):
        body = component.bRepBodies.itemByName('Cylinder {}'.format(index + 1))
        if not body or not body.isSolid:
            raise RuntimeError(case + ': expected solid cylinder')
        x = 1.5 + index * 2.5
        box = body.boundingBox
        actual = [box.minPoint.x, box.minPoint.y, box.minPoint.z,
                  box.maxPoint.x, box.maxPoint.y, box.maxPoint.z]
        expected_bounds = [x - radius, -radius, z, x + radius, radius, z + height]
        if max(abs(a - b) for a, b in zip(actual, expected_bounds)) > 1e-5:
            raise RuntimeError('{}: bounds mismatch: {}'.format(case, actual))
        expected_volume = math.pi * radius * radius * height
        if not math.isclose(body.volume, expected_volume, rel_tol=1e-6, abs_tol=1e-8):
            raise RuntimeError(case + ': cylinder volume mismatch')
        bodies.append({'name': body.name, 'bounds_mm': [v * 10 for v in actual],
                       'volume_mm3': body.volume * 1000})
    return {'counts': counts, 'bodies': bodies, 'fully_constrained_sketches': True,
            'timeline_healthy': True}


def run(context):
    app = adsk.core.Application.get()
    report = {'status': 'running', 'source_sha256': hashlib.sha256(
        Path(__file__).read_bytes()).hexdigest(), 'cases': {}}
    original_document = app.activeDocument
    built = []
    restore_errors = []
    try:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        for case in CASES:
            document, design = build_case(app, case)
            built.append((document, design))
            row = report['cases'][case] = {}
            for label, expressions in STATES:
                for name, expression in expressions.items():
                    design.userParameters.itemByName(name).expression = expression
                row[label] = check_case(design, case)
            app.activeViewport.fit()
        report['status'] = 'passed'
    except Exception:
        report['status'] = 'failed'
        report['error'] = traceback.format_exc()
    finally:
        # Restore parameters in completed cases even if a variant check fails.
        for document, design in built:
            try:
                document.activate()
                for name, expression in STATES[0][1].items():
                    design.userParameters.itemByName(name).expression = expression
                if not design.computeAll():
                    raise RuntimeError('Restore computeAll failed')
            except Exception:
                restore_errors.append(traceback.format_exc())
        if restore_errors:
            report['status'] = 'failed'
            report['restore_errors'] = restore_errors
        if original_document:
            try:
                original_document.activate()
            except Exception:
                report['status'] = 'failed'
                report['reactivation_error'] = traceback.format_exc()
    try:
        REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    except Exception:
        app.userInterface.messageBox('Report write failed:\n' + traceback.format_exc(), 'PlaneSketchTest')
        return
    if report['status'] == 'passed':
        message = ('Three new documents; initial, variant and restored checks passed.\n\n'
                   'A: 3 planes + 3 sketches + 3 extrudes = 9 timeline items\n'
                   'B: 1 plane + 3 sketches + 3 extrudes = 7 timeline items\n'
                   'C: 0 planes + 3 sketches + 3 extrudes = 6 timeline items\n\n'
                   'All three cases produce the same cylinder bounds and volumes.\n')
    else:
        errors = [report.get('error', ''), *restore_errors,
                  report.get('reactivation_error', '')]
        message = ('Test failed. New documents remain available for inspection.\n'
                   + '\n'.join(error for error in errors if error))
    app.userInterface.messageBox(message + '\nReport: ' + str(REPORT), 'PlaneSketchTest')


def stop(context):
    """The test has no persistent commands or event handlers to remove."""
    pass
