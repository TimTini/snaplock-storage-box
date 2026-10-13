"""Five Plane -> Sketch pairs, then one Loft; run directly as an add-in."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import traceback

import adsk.core
import adsk.fusion


DIAMETERS_MM = (20, 30, 18, 28, 16)
DEFAULTS = {'loft_height': '40 mm', 'diameter_scale': '1'}
REPORT = Path(__file__).parent / 'results' / 'last-run.json'


def value(expression):
    return adsk.core.ValueInput.createByString(expression)


def record(report, step, **details):
    report['events'].append({'utc': datetime.now(timezone.utc).isoformat(),
                             'step': step, **details})
    REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')


def inspect(design, sections, label):
    if not design.computeAll():
        raise RuntimeError(label + ': computeAll failed')
    component = design.rootComponent
    counts = {'planes': component.constructionPlanes.count,
              'sketches': component.sketches.count,
              'lofts': component.features.loftFeatures.count,
              'extrudes': component.features.extrudeFeatures.count,
              'bodies': component.bRepBodies.count,
              'timeline': design.timeline.count}
    expected = {'planes': 5, 'sketches': 5, 'lofts': 1,
                'extrudes': 0, 'bodies': 1, 'timeline': 11}
    if counts != expected:
        raise RuntimeError('{}: counts {} expected {}'.format(label, counts, expected))
    timeline = []
    for index in range(design.timeline.count):
        item = design.timeline.item(index)
        entity = item.entity
        timeline.append({'index': index, 'name': entity.name if entity else '',
                         'message': item.errorOrWarningMessage,
                         'healthy': item.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState})
    if not all(row['healthy'] for row in timeline):
        raise RuntimeError(label + ': unhealthy timeline: ' + str(timeline))
    height = design.userParameters.itemByName('loft_height').value
    scale = design.userParameters.itemByName('diameter_scale').value
    measured = []
    for index, (plane, sketch, circle) in enumerate(sections):
        expected_z = 0.5 + height * index / 4
        plane_z = plane.geometry.origin.z
        sketch_z = sketch.sketchToModelSpace(adsk.core.Point3D.create(0, 0, 0)).z
        diameter_mm = circle.radius * 20
        expected_diameter = DIAMETERS_MM[index] * scale
        if max(abs(plane_z - expected_z), abs(sketch_z - expected_z)) > 1e-6:
            raise RuntimeError('{}: section {} position mismatch; plane={}, sketch={}, expected={} cm'.format(
                label, index + 1, plane_z, sketch_z, expected_z))
        if abs(diameter_mm - expected_diameter) > 1e-5 or not sketch.isFullyConstrained:
            raise RuntimeError('{}: section {} diameter={} expected={} mm; fully_constrained={}'.format(
                label, index + 1, diameter_mm, expected_diameter, sketch.isFullyConstrained))
        measured.append({'plane': plane.name, 'sketch': sketch.name,
                         'offset_expression': plane.definition.offset.expression,
                         'plane_z_mm': plane_z * 10, 'sketch_z_mm': sketch_z * 10,
                         'diameter_mm': diameter_mm, 'fully_constrained': True})
    body = component.bRepBodies.item(0)
    if not body.isSolid or body.volume <= 0:
        raise RuntimeError(label + ': expected positive-volume solid')
    bounds = body.boundingBox
    if max(abs(bounds.minPoint.z - 0.5), abs(bounds.maxPoint.z - (0.5 + height))) > 1e-5:
        raise RuntimeError(label + ': solid height mismatch')
    return {'counts': counts, 'timeline': timeline, 'sections': measured,
            'body_z_bounds_mm': [bounds.minPoint.z * 10, bounds.maxPoint.z * 10],
            'volume_mm3': body.volume * 1000}


def run(context):
    app = adsk.core.Application.get()
    report = {'status': 'running', 'source_sha256': hashlib.sha256(
        Path(__file__).read_bytes()).hexdigest(), 'events': []}
    design = None
    try:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        record(report, 'start')
        document = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        document.name = 'LoftSketchTest_5_sections'
        design = adsk.fusion.Design.cast(document.products.itemByProductType('DesignProductType'))
        if not design:
            raise RuntimeError('New document has no Fusion design')
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        for name, expression in DEFAULTS.items():
            design.userParameters.add(name, value(expression),
                                      'mm' if name == 'loft_height' else '', 'Loft demo')
        component = design.rootComponent
        sections = []
        for index, diameter in enumerate(DIAMETERS_MM):
            offset = '5 mm + loft_height * {} / 4'.format(index)
            plane_input = component.constructionPlanes.createInput()
            if not plane_input.setByOffset(component.xYConstructionPlane, value(offset)):
                raise RuntimeError('Plane definition failed')
            plane = component.constructionPlanes.add(plane_input)
            plane.name = 'Plane {:02d}'.format(index + 1)
            record(report, 'plane_created', name=plane.name, expression=offset,
                   timeline_count=design.timeline.count)
            sketch = component.sketches.add(plane)
            sketch.name = 'Section {:02d}'.format(index + 1)
            circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(1.5, 0, 0), diameter / 20)
            circle.centerSketchPoint.isFixed = True
            dimension = sketch.sketchDimensions.addDiameterDimension(
                circle, adsk.core.Point3D.create(1.5 + diameter / 20 + 0.5, 0.5, 0))
            dimension.parameter.expression = '{} mm * diameter_scale'.format(diameter)
            if sketch.profiles.count != 1:
                raise RuntimeError('Expected one closed profile: ' + sketch.name)
            sections.append((plane, sketch, circle))
            record(report, 'sketch_created', name=sketch.name,
                   reference=plane.name, diameter_expression=dimension.parameter.expression,
                   timeline_count=design.timeline.count)
        loft_input = component.features.loftFeatures.createInput(
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        for plane, sketch, circle in sections:
            loft_input.loftSections.add(sketch.profiles.item(0))
        loft_input.isSolid = True
        loft = component.features.loftFeatures.add(loft_input)
        loft.name = 'Loft through all 5 sections'
        record(report, 'loft_created', profiles=[sketch.name for _, sketch, _ in sections],
               timeline_count=design.timeline.count)
        for label, height, scale in [('initial', '40 mm', '1'),
                                     ('variant', '60 mm', '1.2'),
                                     ('restored', '40 mm', '1')]:
            design.userParameters.itemByName('loft_height').expression = height
            design.userParameters.itemByName('diameter_scale').expression = scale
            record(report, label, measurements=inspect(design, sections, label))
        for plane, sketch, circle in sections:
            plane.isLightBulbOn = False
            sketch.isLightBulbOn = False
        app.activeViewport.fit()
        report['status'] = 'passed'
    except Exception:
        report['status'] = 'failed'
        report['error'] = traceback.format_exc()
        if design:
            try:
                for name, expression in DEFAULTS.items():
                    parameter = design.userParameters.itemByName(name)
                    if parameter:
                        parameter.expression = expression
                if not design.computeAll():
                    raise RuntimeError('Parameter restoration: computeAll failed')
                report['restore_compute_completed'] = True
                for index in range(design.timeline.count):
                    item = design.timeline.item(index)
                    if item.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
                        raise RuntimeError('Parameter restoration: timeline item {}: {}'.format(
                            index, item.errorOrWarningMessage))
            except Exception:
                report['restore_error'] = traceback.format_exc()
    try:
        record(report, 'finished', status=report['status'])
    except Exception:
        app.userInterface.messageBox('Report write failed:\n' + traceback.format_exc(), 'LoftSketchTest')
        return
    message = ('5 Plane-Sketch pairs, then 1 Loft.\n'
               'Initial, variant and restored native checks passed.\n'
               'Timeline: 5 planes + 5 sketches + 1 Loft = 11 items.\n'
               'Enable Section sketches in Browser to inspect the cross-sections.')
    if report['status'] != 'passed':
        message = 'Test failed:\n' + report.get('error', '') + report.get('restore_error', '')
    app.userInterface.messageBox(message + '\n\nLog: ' + str(REPORT), 'LoftSketchTest')


def stop(context):
    """This test has no persistent UI controls or event handlers."""
    pass
