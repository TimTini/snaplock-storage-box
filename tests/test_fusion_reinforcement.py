"""Native rib construction formulas match the accepted SCAD specification."""
import importlib.util
import math
from pathlib import Path
import unittest
from types import SimpleNamespace as NS
from unittest.mock import Mock

SCRIPT=Path(__file__).resolve().parents[1]/'fusion/SnaplockStorageBox/SnaplockStorageBox.py'
spec=importlib.util.spec_from_file_location('fusion_ribs',SCRIPT)
model=importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class Reinforcement(unittest.TestCase):
    def test_stations_and_profiles_match_scad_across_sizes(self):
        for length,width,height in [(237.85,123.15,52),(240,220,100),(107.9,30.1,30.2)]:
            p=dict(model.DEFAULTS,length=length,width=width,body_height=height)
            d=model.reinforcement_dimensions(p)
            for axis,span in [('x',length),('y',width)]:
                margin=max(p['corner_radius'],p['wall']+p['rib_thickness']/2)
                count=max(1,math.ceil((span-2*margin)/p['rib_spacing'])-1)
                expected=[margin+(span-2*margin)*i/(count+1) for i in range(1,count+1)]
                self.assertEqual(len(d['stations_'+axis]),len(expected))
                for actual,wanted in zip(d['stations_'+axis],expected):
                    self.assertAlmostEqual(actual,wanted)
            self.assertAlmostEqual(d['top'],height-5)
            self.assertAlmostEqual(d['foot'],min(20,height-5-p['body_floor'],(min(length,width)-6)/4))
            self.assertAlmostEqual(d['depth'],min(5,(height-5-p['body_floor'])/2,(min(length,width)-6)/4))

    def test_three_flags_choose_independent_seed_profiles(self):
        for mask in range(8):
            flags=dict(zip(('wall_ribs','wall_floor_ribs','floor_ribs'),[bool(mask&(1<<i)) for i in range(3)]))
            specs=model.reinforcement_specs(flags)
            self.assertEqual(len(specs),2*sum(flags.values()))
            self.assertEqual({s['family'] for s in specs},{k for k,v in flags.items() if v})

    def test_invalid_clearance_and_spacing_fail_before_document(self):
        for changes in [{'wall_rib_top_clearance':4},{'rib_spacing':2},{'wall_rib_top_clearance':100}]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):
                model.dimensions(dict(model.DEFAULTS,**changes))

    def test_minimum_variant_and_native_corner_domain(self):
        p=dict(model.DEFAULTS,length=107.9,width=30.1,body_height=30.2,lid_height=12.5)
        model.dimensions(p)
        self.assertEqual(model.reinforcement_dimensions(p)['count_y'],1)
        with self.assertRaisesRegex(ValueError,'rounded corners'):
            model.reinforcement_dimensions(dict(p,rib_thickness=20))

    def test_web_offset_and_extrude_follow_both_plane_normals(self):
        for normal in (-1,1):
            for sketch_normal in (-1,1):
                n=NS(profile=Mock(return_value=NS(xDirection=NS(x=1,y=0,z=0),
                    yDirection=NS(x=0,y=0,z=-sketch_normal))),extrude=Mock())
                base=NS(geometry=NS(normal=NS(y=normal)))
                model.rib_extrude(n,object(),base,'rib_margin',[],'rib_thickness','y',0,'seed')
                self.assertEqual(n.profile.call_args.args[1],
                    'rib_margin' if normal>0 else '-(rib_margin)')
                self.assertEqual(n.extrude.call_args.kwargs['negative'],sketch_normal<0)

    def test_seed_only_pattern_binds_model_parameter_after_creation(self):
        n=model.Native.__new__(model.Native)
        inp=NS()
        pattern=NS(quantityOne=NS(expression='2'))
        collection=NS(createInput=Mock(return_value=inp),add=Mock(return_value=pattern))
        n.comp=NS(features=NS(rectangularPatternFeatures=collection))
        n.fusion=NS(PatternDistanceType=NS(SpacingPatternDistanceType=0),
                    PatternComputeOptions=NS(IdenticalPatternCompute=1))
        n.value=lambda expr:expr
        n.objects=lambda items:items
        n.feature=lambda result,name:result
        result=n.rib_pattern(['seed'],'axis','rib_step_x','rib_count_x','pattern')
        self.assertEqual(collection.createInput.call_args.args[2],'2')
        self.assertEqual(inp.quantityTwo,'1')
        self.assertEqual(result.quantityOne.expression,'rib_count_x')


if __name__=='__main__':
    unittest.main()
