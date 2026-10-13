"""Native Parallel Surface Sweep probe for the slot's translating measured arc."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import traceback

REPORT = Path(__file__).parent / 'results/last-run.json'
MEASURED = ((-.383, 15.751), (-.4699, 16.2434), (0, 16.5724))
TOLERANCE_MM = .001


def fix_constant_sketch(sketch):
    """Fix measured curves and their separate sketch points, including arc ends."""
    for collection in (sketch.sketchCurves,sketch.sketchPoints):
        for entity in collection:
            if not entity.isFixed and not entity.isFullyConstrained:
                entity.isFixed = True


def constraint_state(sketch):
    entities = []
    for kind,collection in [('curve',sketch.sketchCurves),('point',sketch.sketchPoints)]:
        for index,entity in enumerate(collection):
            row = {'kind':kind,'index':index,'type':entity.objectType,
                   'fixed':entity.isFixed,'fully_constrained':entity.isFullyConstrained}
            if kind == 'point':
                row['sketch_coordinates_mm'] = [v*10 for v in entity.geometry.asArray()]
            entities.append(row)
    return {'name':sketch.name,'fully_constrained':sketch.isFullyConstrained,
            'constraints':sketch.geometricConstraints.count,
            'dimensions':sketch.sketchDimensions.count,'entities':entities}


def path_angles():
    half_span = math.asin(.8)
    return math.pi/2+half_span,-2*half_span


def circle_geometry():
    (ax, ay), (bx, by), (cx, cy) = MEASURED
    determinant = 2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by))
    lengths = (ax*ax+ay*ay, bx*bx+by*by, cx*cx+cy*cy)
    ox = (lengths[0]*(by-cy)+lengths[1]*(cy-ay)+lengths[2]*(ay-by))/determinant
    oy = (lengths[0]*(cx-bx)+lengths[1]*(ax-cx)+lengths[2]*(bx-ax))/determinant
    angles = [math.atan2(y-oy,x-ox) for x,y in MEASURED]
    sweep = (angles[2]-angles[0]) % math.tau
    if (angles[1]-angles[0]) % math.tau > sweep:
        sweep -= math.tau
    return ox, oy, math.hypot(ax-ox,ay-oy), angles[0], sweep


def surface_point(thickness, z, fraction):
    if not 0 < thickness < 10 or not 0 <= z <= thickness or not 0 <= fraction <= 1:
        raise ValueError('Expected thickness in (0,10), z in [0,t], fraction in [0,1]')
    ox, oy, radius, angle, sweep = circle_geometry()
    c = 2.847-.2976*(5-math.sqrt(25-(z-thickness/2)**2))
    theta = angle+sweep*fraction
    return c+ox+radius*math.cos(theta), oy+radius*math.sin(theta), z


def reference_residual(point, thickness):
    """Distance to the reference arc at clamped Z; conservative surface residual."""
    x,y,z = point
    clipped_z = min(thickness,max(0,z))
    ox,oy,radius,start,sweep = circle_geometry()
    c = 2.847-.2976*(5-math.sqrt(25-(clipped_z-thickness/2)**2))
    theta = math.atan2(y-oy,x-c-ox)
    travelled = (theta-start) % math.tau if sweep > 0 else (start-theta) % math.tau
    fractions = [0,1]
    if travelled <= abs(sweep):
        fractions.append(travelled/abs(sweep))
    return min(math.dist(point,surface_point(thickness,clipped_z,f)) for f in fractions)


def run(context):
    import adsk.core as core
    import adsk.fusion as fusion
    app = core.Application.get()
    report = {'status':'running', 'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'fusion_version':app.version, 'events':[]}
    design = None

    def record(step, **details):
        report['events'].append({'utc':datetime.now(timezone.utc).isoformat(),'step':step,**details})
        REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')

    def feature(result, name):
        if result is None:
            raise RuntimeError('No feature: '+name)
        result.name = name
        record('feature',name=name,health=int(result.healthState),message=result.errorOrWarningMessage)
        if result.healthState != fusion.FeatureHealthStates.HealthyFeatureHealthState:
            raise RuntimeError(name+': '+result.errorOrWarningMessage)
        return result

    try:
        REPORT.parent.mkdir(parents=True,exist_ok=True)
        record('start',scope='Moving arc surface only; thickness through Move and clipping')
        model_path = Path(__file__).parent.parent / 'SnaplockStorageBox/SnaplockStorageBox.py'
        spec = importlib.util.spec_from_file_location('snaplock_sweep_helpers',model_path)
        model = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(model)
        record('helpers',sha256=hashlib.sha256(model_path.read_bytes()).hexdigest())
        document = app.documents.add(core.DocumentTypes.FusionDesignDocumentType)
        document.name = 'SlotSweepTest_parallel_arc'
        design = fusion.Design.cast(document.products.itemByProductType('DesignProductType'))
        if design is None:
            raise RuntimeError('New document has no Fusion design')
        design.designType = fusion.DesignTypes.ParametricDesignType
        value = core.ValueInput.createByString
        parameter = design.userParameters.add('latch_thickness',value('6 mm'),'mm','Test range 5..6.5 mm')
        comp = design.rootComponent
        n = model.Native(design,comp,lambda message:record('native',message=message))
        point = core.Point3D.create

        # The oversized measured curves are constant. Thickness drives downstream
        # features, so Change Parameters exercises genuine native recompute.
        record('build_profile')
        profile_sketch = comp.sketches.add(comp.xYConstructionPlane)
        profile_sketch.name = 'Constant measured arc at oversweep start'
        c = 2.251  # u=-4: 1.359 + .2976*sqrt(25-16).
        points = [point((c+x)/10,y/10,0) for x,y in MEASURED]
        arc = profile_sketch.sketchCurves.sketchArcs.addByThreePoints(*points)
        arc.isFixed = True
        record('constraints_before_fix',sketch=constraint_state(profile_sketch))
        fix_constant_sketch(profile_sketch)
        record('constraints_after_fix',sketch=constraint_state(profile_sketch))
        profile = comp.createOpenProfile(arc,False)
        if profile is None:
            raise RuntimeError('Open arc profile failed')

        record('build_ellipse_path')
        base = comp.xZConstructionPlane
        normal_y = base.geometry.normal.y
        if abs(abs(normal_y)-1) > 1e-8:
            raise RuntimeError('XZ plane normal is not aligned with Y')
        path_plane = n.plane(base,'{} mm'.format(15.751/normal_y),'Path at measured arc Y')
        path_sketch = comp.sketches.add(path_plane)
        path_sketch.name = 'Constant analytic elliptical path'
        def local(x,z):
            return path_sketch.modelToSketchSpace(point(x/10,15.751/10,z/10))
        centre = local(.976,4)
        major = centre.vectorTo(local(.976,9))
        minor = centre.vectorTo(local(.976+1.488,4))
        # Ellipse parameter angle is measured from its major axis, not sketch X.
        # +Z is major, +X is minor: cos(theta) goes -.8 -> +.8 on the right branch.
        ellipse = path_sketch.sketchCurves.sketchEllipticalArcs.addByAngle(
            centre,major,minor,*path_angles())
        if ellipse is None:
            raise RuntimeError('Elliptical arc creation failed')
        ellipse.isFixed = True
        record('constraints_before_fix',sketch=constraint_state(path_sketch))
        fix_constant_sketch(path_sketch)
        record('constraints_after_fix',sketch=constraint_state(path_sketch))
        bounds = ellipse.boundingBox
        record('path_created',sketch_x=list(path_sketch.xDirection.asArray()),
               sketch_y=list(path_sketch.yDirection.asArray()),normal_y=normal_y,
               sketch_bounds_cm=[list(bounds.minPoint.asArray()),list(bounds.maxPoint.asArray())])
        # Model-space sample check catches selecting the ellipse's long branch.
        evaluator = ellipse.worldGeometry.evaluator
        ok, low, high = evaluator.getParameterExtents()
        if not ok:
            raise RuntimeError('Ellipse parameter extents failed')
        for i in range(41):
            ok,p = evaluator.getPointAtParameter(low+(high-low)*i/40)
            if not ok or abs(p.y*10-15.751) > 1e-6 or not -.000001 <= p.z*10 <= 8.000001:
                raise RuntimeError('Ellipse selected wrong branch or plane')
            expected = surface_point(8,min(8,max(0,p.z*10)),0)
            if math.dist(list(p.asArray()),[v/10 for v in expected]) > 1e-6:
                raise RuntimeError('Ellipse differs from analytic endpoint trajectory')
        record('build_parallel_sweep')
        path = comp.features.createPath(ellipse,False)
        sweep_input = comp.features.sweepFeatures.createInput(profile,path,
            fusion.FeatureOperations.NewBodyFeatureOperation)
        sweep_input.isSolid = False
        sweep_input.orientation = fusion.SweepOrientationTypes.ParallelOrientationType
        sweep = feature(comp.features.sweepFeatures.add(sweep_input),'Parallel arc Sweep')
        if sweep.bodies.count != 1:
            raise RuntimeError('Expected one Sweep surface')
        body = sweep.bodies.item(0)
        record('build_parametric_move')
        n.translate(body,'0 mm','0 mm','latch_thickness / 2 - 4 mm','Centre patch on thickness')
        record('build_parametric_top_plane')
        top = n.plane(comp.xYConstructionPlane,'latch_thickness','Top clipping plane')
        for label,plane in [('Bottom',comp.xYConstructionPlane),('Top',top)]:
            record('split',name=label)
            feature(comp.features.splitBodyFeatures.add(
                comp.features.splitBodyFeatures.createInput(body,plane,True)),label+' surface split')
            candidates = list(comp.bRepBodies)
            keep = [b for b in candidates if b.boundingBox.maxPoint.z > 1e-6
                    and b.boundingBox.minPoint.z < (6-1e-5)/10]
            if len(keep) != 1 or len(candidates) != 2:
                raise RuntimeError(label+': unexpected split bodies '+str(len(candidates)))
            body = keep[0]
            discard = next(b for b in candidates if b != body)
            feature(comp.features.removeFeatures.add(discard),label+' excess surface removal')

        def inspect(label):
            record('inspect_start',label=label,expression=parameter.expression)
            if not design.computeAll():
                raise RuntimeError('computeAll failed: '+label)
            thickness = parameter.value*10
            timeline = []
            for i in range(design.timeline.count):
                item = design.timeline.item(i)
                timeline.append({'index':i,'name':item.entity.name if item.entity else '',
                    'healthy':item.healthState == fusion.FeatureHealthStates.HealthyFeatureHealthState,
                    'message':item.errorOrWarningMessage})
            record('timeline',label=label,items=timeline)
            if not all(row['healthy'] for row in timeline):
                raise RuntimeError('Unhealthy timeline: '+label)
            counts = {'planes':comp.constructionPlanes.count,'sketches':comp.sketches.count,
                      'sweeps':comp.features.sweepFeatures.count,'lofts':comp.features.loftFeatures.count,
                      'bodies':comp.bRepBodies.count,'timeline':design.timeline.count}
            record('counts',label=label,counts=counts,
                   constrained=[s.isFullyConstrained for s in (profile_sketch,path_sketch)])
            for sketch in (profile_sketch,path_sketch):
                record('sketch_constraints',label=label,sketch=constraint_state(sketch))
            if counts != dict(planes=2,sketches=2,sweeps=1,lofts=0,bodies=1,timeline=10):
                raise RuntimeError('Unexpected topology/counts: '+str(counts))
            if not all(s.isFullyConstrained for s in (profile_sketch,path_sketch)):
                raise RuntimeError('Constant measured sketches are not fully constrained')
            current = comp.bRepBodies.item(0)
            bounds = current.boundingBox
            if current.isSolid or max(abs(bounds.minPoint.z),abs(bounds.maxPoint.z-thickness/10)) > 1e-6:
                raise RuntimeError('Clipped surface bounds mismatch')
            faces = list(current.faces)
            forward = []
            for iz in range(21):
                for iq in range(11):
                    expected = point(*[v/10 for v in surface_point(thickness,thickness*iz/20,iq/10)])
                    distances = []
                    for face in faces:
                        ev = face.evaluator
                        ok,uv = ev.getParameterAtPoint(expected)
                        if ok and ev.isParameterOnFace(uv):
                            ok,p = ev.getPointAtParameter(uv)
                            if ok:
                                distances.append(p.distanceTo(expected)*10)
                    if not distances:
                        raise RuntimeError('Reference sample has no matching trimmed face')
                    forward.append(min(distances))
            reverse = []
            for face in faces:
                ev = face.evaluator
                limits = ev.parametricRange()
                for iu in range(21):
                    for iv in range(21):
                        uv = core.Point2D.create(limits.minPoint.x+(limits.maxPoint.x-limits.minPoint.x)*iu/20,
                            limits.minPoint.y+(limits.maxPoint.y-limits.minPoint.y)*iv/20)
                        if ev.isParameterOnFace(uv):
                            ok,p = ev.getPointAtParameter(uv)
                            if not ok:
                                raise RuntimeError('Reverse surface evaluation failed')
                            reverse.append(reference_residual([v*10 for v in p.asArray()],thickness))
            if not reverse:
                raise RuntimeError('No reverse samples on trimmed surface')
            record('measurements',label=label,thickness_mm=thickness,faces=len(faces),
                   forward_samples=len(forward),reverse_samples=len(reverse),
                   forward_max_mm=max(forward),reverse_max_mm=max(reverse),tolerance_mm=TOLERANCE_MM)
            if max(forward+reverse) > TOLERANCE_MM:
                raise RuntimeError('Sampled patch residual exceeds tolerance')

        for label,expression in [('initial','6 mm'),('thin','5 mm'),('thick','6.5 mm'),('restored','6 mm')]:
            parameter.expression = expression
            inspect(label)
        report['status'] = 'passed'
        profile_sketch.isLightBulbOn = path_sketch.isLightBulbOn = False
        path_plane.isLightBulbOn = top.isLightBulbOn = False
        app.activeViewport.fit()
    except Exception:
        report['status'] = 'failed'
        report['error'] = traceback.format_exc()
        if design:
            try:
                parameter = design.userParameters.itemByName('latch_thickness')
                if parameter:
                    parameter.expression = '6 mm'
                    report['restore_compute_completed'] = design.computeAll()
            except Exception:
                report['restore_error'] = traceback.format_exc()
    record('finished',status=report['status'])
    message = 'Parallel Sweep patch test: '+report['status']+'\nLog: '+str(REPORT)
    if report['status'] == 'failed':
        message += '\n'+report.get('error','')
    app.userInterface.messageBox(message,'SlotSweepTest')


def stop(context):
    pass
