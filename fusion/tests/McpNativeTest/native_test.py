import adsk.core, adsk.fusion
import json
from pathlib import Path
from itertools import combinations
import hashlib
import importlib.util
from datetime import datetime
from time import perf_counter

def closed_assembly(d):
    p={x:d.userParameters.itemByName(x).value*10 for x in
       ('width','length','body_height','lid_height','layout_gap','mount_end','latch_thickness')}
    tm=adsk.fusion.TemporaryBRepManager.get()
    bodies={name:tm.copy(d.rootComponent.bRepBodies.itemByName(name)) for name in ('Body','Lid','Latch')}
    def transform(body,rows):
        m=adsk.core.Matrix3D.create()
        m.setWithArray([value for row in rows for value in row])
        if not tm.transform(body,m):raise RuntimeError('Temporary assembly transform failed')
    lid_layout=p['width']+p['layout_gap']+18
    transform(bodies['Lid'],[[1,0,0,0],[0,-1,0,(p['width']+lid_layout)/10],
                            [0,0,-1,(p['body_height']+p['lid_height'])/10],[0,0,0,1]])
    latch_layout=2*p['width']+2*p['layout_gap']+36
    seed=bodies.pop('Latch')
    for name,anchor in [('Latch',p['mount_end']),('Latch 2',p['length']-p['mount_end'])]:
        body=tm.copy(seed)
        transform(body,[[1,0,0,(anchor-14)/10],[0,0,1,(p['width']+3-p['latch_thickness']/2)/10],
                        [0,-1,0,(p['body_height']+p['lid_height']-3+latch_layout)/10],[0,0,0,1]])
        bodies[name]=body
    result={}
    for a,b in combinations(bodies,2):
        target=tm.copy(bodies[a])
        ok=tm.booleanOperation(target,bodies[b],adsk.fusion.BooleanTypes.IntersectionBooleanType)
        result[a+' / '+b]={'boolean_success':ok,'faces':target.faces.count,'overlap_mm3':target.volume*1000}
    for pair, row in result.items():
        if not row['boolean_success'] or abs(row['overlap_mm3']) >= .01:
            raise RuntimeError('Closed BRep assembly failed: '+pair+' '+str(row))
    return result


def run(_context: str):
    # Checkout and isolated log folder are supplied by the MCP CLI.
    root=Path(PROJECT_ROOT)
    source=root/'fusion/SnaplockStorageBox/SnaplockStorageBox.py'
    spec=importlib.util.spec_from_file_location('snaplock_mcp_native',source)
    model=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    app=adsk.core.Application.get()
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    lines=['Fusion MCP native validation', 'Fusion version: '+app.version,
           'Script SHA256: '+source_hash, 'Started: '+datetime.now().isoformat()]
    log=Path(RUN_DIRECTORY)/'native-test.log'
    def progress(message):
        lines.append(message)
        log.write_text('\n'.join(lines),encoding='utf-8')
    progress('Validate dimensions')
    model.dimensions(model.DEFAULTS)
    document=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    document.name='Snaplock MCP native validation'
    design=adsk.fusion.Design.cast(app.activeProduct)
    design.designType=adsk.fusion.DesignTypes.ParametricDesignType
    design.unitsManager.distanceDisplayUnits=adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    started=perf_counter()
    progress('Build native bodies')
    model.build(design,progress)
    baseline=model.check_model(design)
    for line in baseline:
        progress('BASELINE '+line)
    model.verify_variants(design,progress)
    rows=[{'name':'baseline','parameters':dict(model.DEFAULTS),'pairs':closed_assembly(design)}]
    variants=[('minimum',{'length':107.9,'width':30.1,'body_height':30.2,'lid_height':11.7}),
              ('lid20',{'lid_height':20}),('lid233.1',{'lid_height':233.1}),
              ('maximum',{'length':250,'width':232.7,'body_height':245.7})]
    saved={key:design.userParameters.itemByName(key).expression for key in model.DEFAULTS}
    try:
        for name,params in variants:
            progress('Verify closed assembly: '+name)
            for key,value in params.items():
                design.userParameters.itemByName(key).expression=str(value)+' mm'
            model.check_model(design)
            rows.append({'name':name,'parameters':params,'pairs':closed_assembly(design)})
            for key,expr in saved.items():
                design.userParameters.itemByName(key).expression=expr
            model.check_model(design)
    finally:
        for key,expr in saved.items():
            design.userParameters.itemByName(key).expression=expr
        model.check_model(design)
    output=source.parent/'exports'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    progress('Export native STL files')
    model.export_meshes(design,adsk.fusion,output)
    archive=design.exportManager.createFusionArchiveExportOptions(str(output/'SnaplockStorageBox.f3d'))
    if not design.exportManager.execute(archive):
        raise RuntimeError('Fusion archive export failed')
    app.activeViewport.fit()
    app.activeViewport.saveAsImageFile(str(output/'native-preview.png'),1280,960)
    report={'scope':'native build/recompute and closed BRep assembly; external STL audit and physical print are separate',
            'fusion_version':app.version,'script_sha256':source_hash,
            'wrapper_sha256':hashlib.sha256((root/'fusion/tests/McpNativeTest/native_test.py').read_bytes()).hexdigest(),
            'parameters_mm':dict(model.DEFAULTS),'reinforcement':dict(model.BUILD_RIBS),
            'baseline_checks':baseline,'closed_assembly_cases':rows,
            'planes':design.rootComponent.constructionPlanes.count,
            'sketches':design.rootComponent.sketches.count,'timeline':design.timeline.count,
            'elapsed_seconds':perf_counter()-started}
    (output/'native-test.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    progress('NATIVE_BUILD_RECOMPUTE_ASSEMBLY_OK: '+str(output))
    print(json.dumps({'status':'native_build_recompute_assembly_ok','output':str(output)}))
