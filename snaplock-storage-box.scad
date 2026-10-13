// Snaplock box: measured reconstruction of source STL, dimensions in mm.
// Source SHA256 73faaa2d438b02038b9f84002202435973a09f92ec2a48315577e0e00baea167
// Local X follows shell length; Y=0 is the rear wall; Z=0 is the print bed.

/* [Main dimensions] */
// Shared shell length for body and lid (mm).
length = 237.85;
// Shared shell width for body and lid (mm).
width = 123.15;
// Body height (mm).
body_height = 52;

/* [Lid and shell details] */
// Lid height (mm).
lid_height = 15;
wall = 3;
body_floor = 2;
lid_floor = 3;
corner_radius = 12;
body_inner_radius = 8;
bottom_bevel = 5;
body_inner_bevel = 4.7;
/* [Mechanism] */
mount_end = 32.9;
pin_radius = 5;
latch_ball_radius = 3.75;
fit_clearance = 0;
latch_thickness = 6;
/* [Internal reinforcement] */
// Independent switches: wall uprights, wall-to-floor feet, and floor grid.
wall_ribs = false;
wall_floor_ribs = false;
floor_ribs = false;
// Maximum distance between centred rib stations (mm).
rib_spacing = 45;
rib_thickness = 2.4;
floor_rib_height = 4;
// Upright wall projection and width of the 45-degree foot (mm).
wall_rib_depth = 5;
wall_rib_foot = 20;
// Clearance below the body rim; 5 mm clears the current lid's closed envelope.
wall_rib_top_clearance = 5;
/* [Print layout] */
part = "layout"; // [layout,body,lid,latch]
layout_gap = 20;
/* [Resolution] */
$fn = 96;
/* [Hidden] */
eps = 0.001;
bevel_height = bottom_bevel*sqrt(3);
lid_inner_bevel = bottom_bevel-wall+lid_floor/sqrt(3);
// Preserve the mating head/catch shapes while the connecting span follows the lid.
latch_span_delta = lid_height-15;
// Circumscribe the sampled pocket around the analytic ball for arbitrary rotation.
// Two angular half-steps bound the latitude/longitude facet sagitta.
pin_pocket_radius = (pin_radius+fit_clearance)/pow(cos(180/$fn),2);

assert(length>2*(mount_end+21) && width>2*corner_radius+2*wall);
assert(body_height>body_floor+body_inner_bevel*sqrt(3)+20);
assert(lid_height>lid_floor+lid_inner_bevel*sqrt(3));
assert(corner_radius>bottom_bevel && body_inner_radius>body_inner_bevel);
assert(wall>0 && body_floor>0 && lid_floor>0 && fit_clearance>=0);
assert(latch_thickness>=5 && latch_thickness<=6.5);
assert(bottom_bevel>0 && body_inner_bevel>0 && lid_inner_bevel>0);
assert(wall<corner_radius && lid_inner_bevel<corner_radius-wall);
assert(lid_height>bevel_height+3 && fit_clearance<=0.5);
assert(mount_end>=corner_radius+20 && layout_gap>=0);
assert(pin_radius>4.5 && pin_radius<=5.5 && latch_ball_radius>=3.5 && latch_ball_radius<=4);
assert($fn>=32);
assert(is_bool(wall_ribs) && is_bool(wall_floor_ribs) && is_bool(floor_ribs));
assert(rib_thickness>0 && rib_spacing>rib_thickness);
assert(floor_rib_height>0 && floor_rib_height<body_height-body_floor-20);
assert(wall_rib_depth>0 && wall_rib_foot>0);
assert(wall_rib_top_clearance>=5 && wall_rib_top_clearance<body_height-body_floor);

// Circular arcs through measured start, middle and end. Used only for local profiles.
function cross2(a,b) = a[0]*b[1]-a[1]*b[0];
function arc(a,m,b,n=24) =
    let(u=m-a,v=b-a,d=2*cross2(u,v),
        c=a+[(u*u*v[1]-v*v*u[1])/d,(u[0]*v*v-v[0]*u*u)/d],
        t=atan2(a[1]-c[1],a[0]-c[0]),
        tm=(atan2(m[1]-c[1],m[0]-c[0])-t+360)%360,
        tb=(atan2(b[1]-c[1],b[0]-c[0])-t+360)%360,
        sweep=tm<=tb ? tb : tb-360,r=norm(a-c))
    [for(i=[0:n-1]) c+r*[cos(t+sweep*i/n),sin(t+sweep*i/n)]];

module rounded(inset,r) {
    translate([inset,inset]) offset(r=r)
        translate([r,r]) square([length-2*(inset+r),width-2*(inset+r)]);
}

module bevel(z0,z1,inset0,inset1,r0,r1) {
    hull() {
        translate([0,0,z0]) linear_extrude(eps) rounded(inset0,r0);
        translate([0,0,z1-eps]) linear_extrude(eps) rounded(inset1,r1);
    }
}

module shell_blank(lid=false) {
    h=lid?lid_height:body_height;
    union() {
        bevel(0,bevel_height,bottom_bevel,0,corner_radius-bottom_bevel,corner_radius);
        translate([0,0,bevel_height-eps]) linear_extrude(h-bevel_height+eps) rounded(0,corner_radius);
    }
}

module cavity(lid=false) {
    h=lid?lid_height:body_height;
    f=lid?lid_floor:body_floor;
    b=lid?lid_inner_bevel:body_inner_bevel;
    r=lid?corner_radius-wall:body_inner_radius;
    inner_top=f+b*sqrt(3);
    bevel(f,inner_top,wall+b,wall,r-b,r);
    translate([0,0,inner_top-eps]) linear_extrude(h-inner_top+6) rounded(wall,r);
}

// Extrude a YZ profile along the length (X).
module web(x,span,points) {
    translate([x,0,0]) multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
        linear_extrude(span) polygon(points);
}

module body_mount() {
    h=body_height;
    difference() {
        intersection() {
            web(-22,11,concat([[1,h-15],[0,h-15]],
                arc([-8.3045298,h-2.3297678],[-4.75,h+4.25],[-0.5,h]),[[ -0.5,h],[1,h]]));
            linear_extrude(h+5) polygon([[-21.2757,1],[-20.2757,0],[-18.7035,-1.5723],
                [-19.2757+10*tan(20),-10],[-11,-10],[-11,1]]);
        }
        translate([-7,-4.75,h]) sphere(pin_pocket_radius);
    }
    difference() {
        intersection() {
            web(-22,13.1,concat([[width-1,h-19],[width,h-19],
                [width+2.8113,h-15.7393],[width+5.4796,h-12.3605],[width+8,h-8.8701]],
                arc([width+8,h-1],[width+7.7071068,h-0.2928932],[width+7,h]),
                [[width+7,h],[width-1,h]]));
            linear_extrude(h+5) polygon([[-21.3,width-1],[-20.9,width],[-17.75,width+8],
                [-8.9,width+8],[-8.9,width-1]]);
            union() {
                translate([-22,width-2,0]) cube([9.25,12,h+5]);
                translate([-12.75,width+3,h+9]) rotate([0,90,0])
                    difference() {
                        cylinder(h=3.734,r1=9.486833+3.734*tan(50),r2=9.486833);
                        translate([0,0,-eps]) cylinder(h=3.734+2*eps,r=9.5);
                    }
            }
        }
        // Source pocket is a vertical R5 bore with 1 mm conical end chamfers.
        translate([-8.75,width+3,h-11.5]) {
            cylinder(h=1,r1=4,r2=5);
            translate([0,0,1]) cylinder(h=4.5,r=5);
            translate([0,0,5.5]) cylinder(h=1,r1=5,r2=4);
        }
    }
}

module lid_mount() {
    h=lid_height;
    difference() {
        intersection() {
            web(-21,12,concat([[5,0],[-5.1423,0]],
                arc([-5.1423,0],[-7.5175,3.3922],[-8,6.1284]),[[-8,6.1284],[-8,h-0.9377]],
                arc([-8,h-0.9377],[-3,h+0.486833],[0,h]),[[0,h],[1,h],[5,8.660254]]));
            linear_extrude(h+1) polygon([[-21,5],[-21,0],[-17.75,-8],[-9,-8],[-9,5]]);
            union() {
                translate([-22,-9,0]) cube([9.25,15,h]);
                intersection() {
                    translate([-12.75,-3,6]) rotate([0,90,0]) difference() {
                        cylinder(h=3.734,r=9.5);
                        translate([0,0,-eps]) cylinder(h=3.734+2*eps,
                            r1=9.486833-3.734*tan(50)-eps*tan(50),r2=9.486833+eps*tan(50));
                    }
                    translate([-13,-9,6]) cube([5,15,h]);
                }
            }
        }
        translate([-10.5,-3,6]) sphere(latch_ball_radius+fit_clearance);
    }
    intersection() {
        web(-10.75,10,concat([[width-5,0],[width-1.1,0],
            [width+0.5968,1.0901],[width+2.072,2.3838],[width+3.3657,3.859],
            [width+4.4558,5.4904],[width+8.6471,h-2.25]],
            arc([width+8.6471,h-2.25],[width+4.75,h+4.5],[width+0.25,h]),
            [[width+0.25,h],[width-1,h],[width-5,8.660254]]));
        linear_extrude(h+5) polygon([[-10.75,width-5],[-2.3833,width-5],[-2.3833,width],
            [-2.3833-10*tan(20),width+10],[-10.75,width+10]]);
    }
    intersection() {
        translate([-7,width+4.75,h]) sphere(pin_radius);
        translate([-15,width+4.75,h]) rotate([0,90,0]) cylinder(h=30,r=4.5);
        translate([-13,width-1,h-5]) cube([2.25+eps,11,10]);
    }
}

function rib_stations(span) =
    let(margin=max(corner_radius,wall+rib_thickness/2),
        count=max(1,ceil((span-2*margin)/rib_spacing)-1))
    [for(i=[1:count]) margin+(span-2*margin)*i/(count+1)];

module internal_reinforcement() {
    if(floor_ribs || wall_ribs || wall_floor_ribs) intersection() {
        // Clip additions to the original outside shell, retaining its envelope.
        shell_blank();
        union() {
            if(floor_ribs) {
                for(x=rib_stations(length))
                    translate([x-rib_thickness/2,wall-eps,body_floor-eps])
                        cube([rib_thickness,width-2*wall+2*eps,floor_rib_height+eps]);
                for(y=rib_stations(width))
                    translate([wall-eps,y-rib_thickness/2,body_floor-eps])
                        cube([length-2*wall+2*eps,rib_thickness,floor_rib_height+eps]);
            }
            if(wall_ribs || wall_floor_ribs) {
                top=body_height-wall_rib_top_clearance;
                foot=min(wall_rib_foot,top-body_floor,(min(length,width)-2*wall)/4);
                depth=min(wall_rib_depth,(top-body_floor)/2,(min(length,width)-2*wall)/4);
                profiles=concat(
                    wall_ribs ? [[[wall-eps,body_floor-eps],[wall+depth,body_floor-eps],
                                  [wall+depth,top-depth],[wall-eps,top]]] : [],
                    wall_floor_ribs ? [[[wall-eps,body_floor-eps],[wall+foot,body_floor-eps],
                                        [wall-eps,body_floor+foot]]] : []);
                for(profile=profiles) {
                    for(x=rib_stations(length)) for(s=[0,1])
                        translate([0,s*width,0]) mirror([0,s,0])
                            web(x-rib_thickness/2,rib_thickness,profile);
                    for(y=rib_stations(width)) for(s=[0,1])
                        translate([s*length,0,0]) mirror([s,0,0])
                            multmatrix([[0,1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]])
                                web(y-rib_thickness/2,rib_thickness,profile);
                }
            }
        }
    }
}

module box(lid=false) {
    union() {
        difference() {
            union() {
                shell_blank(lid);
                for(x=[mount_end,length-mount_end])
                    translate([x,0,0]) for(s=[-1,1]) scale([s,1,1])
                        if(lid) lid_mount(); else body_mount();
            }
            cavity(lid);
        }
        if(!lid) internal_reinforcement();
    }
}

// R5 relief across thickness. Local blend coefficients approximate measured
// Z=0.1/3/5.9 source sections; whole-part differences are recorded by the audit.
function relief(z) = 5-sqrt(25-pow(z-latch_thickness/2,2));
function slot_front_reference(z) = let(d=relief(z),c=2.847-0.2976*d)
    concat([[-2,7.9971-d],[1.5,7.9971-d],[5.234,12.4458-0.488*d]],
        arc([c-0.383,15.751],[c-0.4699,16.2434],[c,16.5724]),[[c,16.5724]],
        arc([4.5,16.5724],[4.8535534,16.7188466],[5,17.0724]),
        [[5,17.0724],[3.5,17.0724],[1.5+1.35*d,17.0724],[0.5+d,18.0724],[-2,18.0724]]);
function slot_front_profile(z) = [for(p=slot_front_reference(z)) p+[0,latch_span_delta]];
function slot_fixed_reference() = concat([[3.5,17.0724-eps],[5,17.0724-eps],[5,17.0724]],
    arc([5,26.0724],[4.5,26.5724],[4,26.0724]),[[4,26.0724],[4,17.5724]],
    arc([4,17.5724],[3.8535534,17.2188466],[3.5,17.0724]),[[3.5,17.0724]]);
function slot_fixed_profile() = [for(p=slot_fixed_reference()) p+[0,latch_span_delta]];

// Local changing profiles keep the spring relief editable without a mesh import.
function signed_area(p,i=0) = i==len(p) ? 0 : cross2(p[i],p[(i+1)%len(p)])+signed_area(p,i+1);
module profile_loft(profiles,zs) {
    n=len(profiles[0]); k=len(zs);
    // OpenSCAD polyhedra use clockwise faces when viewed from outside.
    rings=signed_area(profiles[0])>0 ? [for(p=profiles) [for(j=[n-1:-1:0]) p[j]]] : profiles;
    polyhedron(points=[for(i=[0:k-1]) for(p=rings[i]) [p[0],p[1],zs[i]]],
        faces=concat([[for(j=[n-1:-1:0]) j]],[[for(j=[0:n-1]) (k-1)*n+j]],
            [for(i=[0:k-2]) for(j=[0:n-1])
                [i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j]]));
}

// A revolved R2 round at the ends of the R5 notch cylinder.
module notch_tool() {
    translate([6.5,3,latch_thickness/2]) rotate([0,90,0]) rotate_extrude()
        polygon(concat([[0,0],[3,0]],arc([3,0],[4.41421356,0.58578644],[5,2]),
            [[5,2],[5,13]],arc([5,13],[4.41421356,14.41421356],[3,15]),[[3,15],[0,15]]));
}

// R5 tip, elliptical shoulder (Rx=6.75, Rz=5), and two short convex blends.
// Hull blends approximate the original ruled surface; measured by audit-catch-csg.py.
module latch_tooth() {
    module section(y,x,x_scale=1) {
        translate([x,y,latch_thickness/2]) rotate([-90,0,0])
            scale([x_scale,1,1]) cylinder(h=eps,r=5);
    }
    translate([0,latch_span_delta,0]) intersection() {
        translate([-2,17.0724,0]) cube([5.5,6,latch_thickness]);
        union() {
            hull() {
                section(17.0724,8.25,1.35);
                section(18.0724-eps,5.5);
            }
            translate([5.5,18.0724-eps,latch_thickness/2]) rotate([-90,0,0])
                cylinder(h=4+2*eps,r=5);
            hull() {
                section(22.0724,5.5);
                section(23.0724-eps,8.25,1.35);
            }
        }
    }
}

module latch() {
    // Eight sections follow the R5 angle; the fixed rear channel is extruded.
    angle = asin(latch_thickness/10);
    zs=[for(i=[0:7]) latch_thickness/2+5*sin(angle*(2*i/7-1))];
    difference() {
        intersection() {
            union() {
                translate([1.5,0,0]) cube([25,32.9+latch_span_delta,latch_thickness]);
                for(s=[0,1]) translate([28*s,0,0]) mirror([s,0,0]) {
                    translate([3.75,3,latch_thickness/2]) sphere(latch_ball_radius);
                    latch_tooth();
                }
            }
            translate([-2,0,0]) cube([32,35+latch_span_delta,latch_thickness]);
            union() {
                translate([-2,5,latch_thickness/2]) rotate([0,90,0]) cylinder(h=32,r=5);
                translate([-2,3,0]) cube([32,32+latch_span_delta,latch_thickness]);
            }
        }
        notch_tool();
        for(s=[0,1]) translate([28*s,0,0]) mirror([s,0,0])
            intersection() {
                // Keep the ball supports through Y=7 when shortening the span.
                translate([-3,latch_span_delta<0?7:-eps,-eps])
                    cube([34,40+abs(latch_span_delta),latch_thickness+2*eps]);
                union() {
                    // The lid-side lip remains at the head; its clearance ends
                    // before the moving catch. The body-side clearance follows it.
                    intersection() {
                        profile_loft([for(z=concat([-eps],zs,[latch_thickness+eps]))
                            slot_front_reference(min(latch_thickness,max(0,z)))],concat([-eps],zs,[latch_thickness+eps]));
                        translate([-3,-eps,-eps])
                            cube([34,17.0724+min(0,latch_span_delta)+eps,latch_thickness+2*eps]);
                    }
                profile_loft([for(z=concat([-eps],zs,[latch_thickness+eps]))
                    slot_front_profile(min(latch_thickness,max(0,z)))],concat([-eps],zs,[latch_thickness+eps]));
                translate([0,0,-eps]) linear_extrude(latch_thickness+2*eps) polygon(slot_fixed_profile());
                }
            }
        web(-2,32,[[26.9+latch_span_delta,latch_thickness],[31.835144+latch_span_delta,latch_thickness-4.935139],
            [31.743874+latch_span_delta,0],[35+latch_span_delta,0],[35+latch_span_delta,latch_thickness]]);
    }
}

if(part=="body") box();
else if(part=="lid") box(true);
else if(part=="latch") latch();
else if(part=="layout") {
    color("steelblue") box();
    translate([0,width+layout_gap+17,0]) color("lightblue") box(true);
    for(i=[0:1]) translate([length+layout_gap,(45+max(0,latch_span_delta))*i,0]) color("orange") latch();
} else assert(false,"Unknown part; select layout, body, lid or latch");
