"""Regression: lid height updates the latch span and matching hinge anchors."""
import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('assembly_regression',ROOT/'tools/audit-latch-fit.py')
fit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(fit)


@unittest.skipUnless(shutil.which(os.environ.get('OPENSCAD','openscad')), 'Set OPENSCAD to run geometry integration')
class ScadAssembly(unittest.TestCase):
    def test_minimum_and_tall_lids_clear_all_closed_pairs(self):
        with tempfile.TemporaryDirectory() as directory:
            for height in (11.7,15,20):
                with self.subTest(lid_height=height):
                    output=Path(directory)/str(height);output.mkdir()
                    definitions=['length=107.9','width=30.1','body_height=30.2','lid_height='+str(height)]
                    meshes={name:fit.audit.build(name,output/(name+'.stl'),definitions)
                            for name in ('body','lid','latch')}
                    for mesh in meshes.values():
                        self.assertTrue(mesh.is_volume)
                        self.assertEqual(len(mesh.split()),1)
                    lid=fit.closed_lid(meshes['lid'],30.1,30.2,height)
                    latch=fit.installed_latch(meshes['latch'],32.9,30.1,30.2,height)
                    for a,b in [(meshes['body'],lid),(meshes['body'],latch),(lid,latch)]:
                        self.assertLess(abs((fit.solid(a)^fit.solid(b)).volume()),.01)

    def test_tall_lid_uses_the_exported_mating_datum(self):
        with tempfile.TemporaryDirectory() as directory:
            definitions=['length=240','width=120','body_height=50','lid_height=233.1']
            body=fit.audit.build('body',Path(directory)/'body.stl',definitions)
            lid=fit.audit.build('lid',Path(directory)/'lid.stl',definitions)
            placed=fit.closed_lid(lid,120,50,233.1)
            self.assertLess(abs((fit.solid(body)^fit.solid(placed)).volume()),.01)

    def test_pin_clears_pocket_during_opening(self):
        with tempfile.TemporaryDirectory() as directory:
            definitions=['length=107.9','width=30.1','body_height=30.2','lid_height=11.7']
            body=fit.audit.build('body',Path(directory)/'body.stl',definitions)
            lid=fit.audit.build('lid',Path(directory)/'lid.stl',definitions)
            placed=fit.closed_lid(lid,30.1,30.2,11.7)
            placed.apply_transform(fit.trimesh.transformations.rotation_matrix(
                fit.np.radians(90),[1,0,0],[0,-4.75,30.2]))
            self.assertLess(abs((fit.solid(body)^fit.solid(placed)).volume()),.01)

    def test_pocket_compensation_follows_mesh_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            for facets in (32,96,192):
                output=Path(directory)/str(facets);output.mkdir()
                definitions=['length=107.9','width=30.1','body_height=30.2',f'$fn={facets}']
                body=fit.audit.build('body',output/'body.stl',definitions)
                lid=fit.audit.build('lid',output/'lid.stl',definitions)
                for angle in (0,15,45,90,110):
                    with self.subTest(facets=facets,angle=angle):
                        placed=fit.closed_lid(lid,30.1,30.2,15)
                        placed.apply_transform(fit.trimesh.transformations.rotation_matrix(
                            fit.np.radians(angle),[1,0,0],[0,-4.75,30.2]))
                        self.assertLess(abs((fit.solid(body)^fit.solid(placed)).volume()),.01)


if __name__=='__main__':
    unittest.main()
