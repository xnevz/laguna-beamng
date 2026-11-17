"""Generate the BeamNG vehicle files for the Renault Laguna II (X74) from one spec.

Run:  python tools/beamng/gen_laguna2.py        (then: python tools/beamng/validate.py)

Writes vehicles/renault_laguna/:
    renault_laguna.jbeam          main part (slot tree root)
    laguna2_body.jbeam            liftback body: chassis nodes/beams/triangles, body meshes
    laguna2_suspension.jbeam      front MacPherson / rear torsion-beam variants, brakes, steering
    laguna2_wheels.jbeam          wheel + tyre options
    laguna2_engines.jbeam         the real Laguna II engine range
    laguna2_transmissions.jbeam   gearboxes (per engine family) and differentials
    laguna2_exterior.jbeam        lights, glass, mirrors, wiper, mouldings, plates, badges...
    info.json, *.pc, info_*.json  factory paints and configurations

Coordinate frame = Blender scene = BeamNG vehicle frame: front of the car
towards -Y, +X is the car's left, Z up, ground at Z = 0.  Every option in the
customisation spec (BEAMNG_CUSTOMIZATION_OPTIONS.md) that is implemented here
is listed in CUSTOMIZATION_STATUS.md.
"""

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "vehicles", "renault_laguna")
AUTHORS = "Abdelkarim & Claude"
MODEL = "renault_laguna"

# --------------------------------------------------------------------------
# Car geometry (metres) - shared with tools/laguna2 (refmodel.py / build.py)
# --------------------------------------------------------------------------
HALF = 4.576 / 2
Y_AXLE_F = 0.965 - HALF          # -1.323
Y_AXLE_R = 0.985 + 2.748 - HALF  # +1.445
WHEEL_R = 0.317
TRACK_F = 0.757                  # half track
TRACK_R = 0.745

# Corner loads carried by each spring (N), from the node masses
# minus the unsprung mass at that corner (1305 kg / 61.6 % front = the node masses
# of the standard car, see the weights in chassis_nodes).  Used for the spring preload so the car
# sits at its design ride height whatever spring rate is dialled in.
LOAD_F = (1305 * 0.616 / 2 - 22) * 9.81
LOAD_R = (1305 * 0.384 / 2 - 20) * 9.81


def S(v):
    return "l" if v > 0 else "r"


# --------------------------------------------------------------------------
# Chassis
# --------------------------------------------------------------------------
# station: (y, (lower z, lower half-width), (belt z, belt half-width))
STATIONS = [
    (-2.20, (0.34, 0.55), (0.62, 0.62)),   # 0 front bumper
    (-1.85, (0.30, 0.60), (0.70, 0.74)),   # 1 front crossmember / headlamps
    (-1.32, (0.30, 0.48), (0.80, 0.80)),   # 2 front strut towers (inboard of the wheels)
    (-0.85, (0.26, 0.72), (0.90, 0.80)),   # 3 firewall / A-pillar foot
    (-0.15, (0.24, 0.74), (0.92, 0.82)),   # 4 B-pillar
    (0.55, (0.24, 0.74), (0.94, 0.82)),    # 5 rear door / rear seat
    (1.05, (0.26, 0.70), (0.96, 0.80)),    # 6 front of the rear arch
    (1.45, (0.30, 0.48), (0.96, 0.80)),    # 7 rear shock towers (inboard of the wheels)
    (1.95, (0.32, 0.62), (0.94, 0.76)),    # 8 rear panel
    (2.22, (0.36, 0.58), (0.70, 0.66)),    # 9 rear bumper
]
ROOF = [(-0.30, 1.36, 0.58), (0.55, 1.42, 0.60), (1.20, 1.36, 0.55)]   # r1 (windscreen top) .. r3 (rear glass top)
ENGINE = [("e1l", 0.30, -1.66, 0.40), ("e1r", -0.30, -1.66, 0.40), ("e2l", 0.30, -1.40, 0.72), ("e2r", -0.30, -1.40, 0.72)]


def lo(i, s):
    return f"b{i}f{s}"


def mid(i, s):
    return f"b{i}m{s}"


def roof(i, s):
    return f"r{i + 1}{s}"


def chassis_nodes():
    rows = [["id", "posX", "posY", "posZ"],
            {"nodeMaterial": "|NM_METAL"}, {"frictionCoef": 0.5}, {"collision": True}, {"selfCollision": True},
            {"group": "laguna2_body"}]
    # Node weights fall off from the engine bay to the tail so the car carries
    # ~60 % on the front axle like the real (front-engined) Laguna II.
    for level, base in (("f", (24, 24, 24, 24, 20, 19, 18, 17, 15, 14)), ("m", (16, 17, 18, 17, 16, 15, 14, 13, 12, 11))):
        for i, (y, (zl, wl), (zm, wm)) in enumerate(STATIONS):
            rows.append({"nodeWeight": base[i]})
            for sx in (1, -1):
                if level == "f":
                    rows.append([lo(i, S(sx)), round(sx * wl, 3), y, zl])
                else:
                    rows.append([mid(i, S(sx)), round(sx * wm, 3), y, zm])
    rows.append({"nodeWeight": 9})
    for i, (y, z, w) in enumerate(ROOF):
        for sx in (1, -1):
            rows.append([roof(i, S(sx)), round(sx * w, 3), y, z])
    rows += [{"nodeWeight": 46}, {"group": ["laguna2_body", "laguna2_engine"]}]   # engine + gearbox ~185 kg
    for n, x, y, z in ENGINE:
        rows.append([n, x, y, z])
    rows.append({"group": ""})
    return rows


def chassis_beams():
    B = [["id1:", "id2:"],
         {"beamPrecompression": 1, "beamType": "|NORMAL", "beamLongBound": 1, "beamShortBound": 1},
         {"beamSpring": 2600000, "beamDamp": 160}, {"beamDeform": 90000, "beamStrength": "FLT_MAX"}]
    n = len(STATIONS)
    cage = []
    for i in range(n):
        cage += [[lo(i, "l"), lo(i, "r")], [mid(i, "l"), mid(i, "r")]]
        for s in "lr":
            cage.append([lo(i, s), mid(i, s)])
        if i + 1 < n:
            for s in "lr":
                cage += [[lo(i, s), lo(i + 1, s)], [mid(i, s), mid(i + 1, s)],
                         [lo(i, s), mid(i + 1, s)], [mid(i, s), lo(i + 1, s)]]
            cage += [[lo(i, "l"), lo(i + 1, "r")], [lo(i, "r"), lo(i + 1, "l")],
                     [mid(i, "l"), mid(i + 1, "r")], [mid(i, "r"), mid(i + 1, "l")]]
        cage += [[lo(i, "l"), mid(i, "r")], [lo(i, "r"), mid(i, "l")]]
    # Roof, pillars and the cage diagonals that keep the cabin square.
    for i in range(len(ROOF)):
        cage.append([roof(i, "l"), roof(i, "r")])
        if i + 1 < len(ROOF):
            for s in "lr":
                cage.append([roof(i, s), roof(i + 1, s)])
            cage += [[roof(i, "l"), roof(i + 1, "r")], [roof(i, "r"), roof(i + 1, "l")]]
    for s in "lr":
        o = "r" if s == "l" else "l"
        cage += [[mid(3, s), roof(0, s)], [mid(4, s), roof(0, s)], [mid(4, s), roof(1, s)],   # A and B pillars
                 [mid(5, s), roof(1, s)], [mid(6, s), roof(2, s)], [mid(7, s), roof(2, s)],   # C pillar
                 [mid(8, s), roof(2, s)],                                                    # tailgate edge
                 [lo(3, s), roof(0, s)], [lo(5, s), roof(1, s)], [lo(7, s), roof(2, s)],     # cage diagonals
                 [mid(3, s), roof(0, o)], [mid(5, s), roof(1, o)], [mid(7, s), roof(2, o)]]
    B += cage
    # Engine block (rigid) and its mounts.
    B += [{"beamSpring": 8000000, "beamDamp": 250}, {"beamDeform": "FLT_MAX", "beamStrength": "FLT_MAX"}]
    names = [e[0] for e in ENGINE]
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            B.append([names[a], names[b]])
    B += [{"beamSpring": 1500000, "beamDamp": 120}, {"beamDeform": 60000, "beamStrength": 220000}]
    for e in names:
        s = e[-1]
        for t in (lo(1, s), mid(1, s), lo(2, s), mid(2, s), lo(1, "r" if s == "l" else "l")):
            B.append([e, t])
    B.append({"beamPrecompression": 1, "beamDeform": 90000, "beamStrength": "FLT_MAX"})
    return B


def quad(a, b, c, d):
    return [[a, b, c], [a, c, d]]


def chassis_triangles():
    T = [["id1:", "id2:", "id3:"], {"groundModel": "metal"}, {"dragCoef": 8}]
    n = len(STATIONS)
    for i in range(n - 1):
        T += quad(lo(i, "l"), lo(i + 1, "l"), mid(i + 1, "l"), mid(i, "l"))          # left side
        T += quad(lo(i, "r"), mid(i, "r"), mid(i + 1, "r"), lo(i + 1, "r"))          # right side
        T += quad(lo(i, "l"), lo(i, "r"), lo(i + 1, "r"), lo(i + 1, "l"))            # floor
    for i in (0, 1, 2, 7, 8):
        T += quad(mid(i, "l"), mid(i + 1, "l"), mid(i + 1, "r"), mid(i, "r"))        # hood / rear deck
    T += quad(lo(0, "l"), mid(0, "l"), mid(0, "r"), lo(0, "r"))                       # nose
    T += quad(lo(n - 1, "r"), mid(n - 1, "r"), mid(n - 1, "l"), lo(n - 1, "l"))       # tail
    T += quad(mid(3, "l"), roof(0, "l"), roof(0, "r"), mid(3, "r"))                   # windscreen
    for i in range(len(ROOF) - 1):
        T += quad(roof(i, "l"), roof(i + 1, "l"), roof(i + 1, "r"), roof(i, "r"))   # roof
    T += quad(roof(2, "l"), mid(8, "l"), mid(8, "r"), roof(2, "r"))                   # rear glass
    return T


# --------------------------------------------------------------------------
# Suspension (one degree of freedom per corner)
# --------------------------------------------------------------------------
def corner(axle, sx):
    """Nodes of one corner: hub axis, knuckle, and the body-side pivots."""
    y0 = Y_AXLE_F if axle == "f" else Y_AXLE_R
    tr = TRACK_F if axle == "f" else TRACK_R
    s = S(sx)
    p = axle  # node prefix
    k = {
        f"{p}w1{s}": (sx * (tr - 0.10), y0, WHEEL_R),             # inner hub
        f"{p}w2{s}": (sx * (tr + 0.04), y0, WHEEL_R),             # outer hub
        f"{p}h1{s}": (sx * (tr - 0.10), y0, 0.14),                # lower ball joint
        f"{p}h2{s}": (sx * (tr - 0.16), y0 + 0.02, 0.52),         # upper knuckle (strut / upper link)
        f"{p}k1{s}": (sx * (tr - 0.15), y0 + 0.14, 0.26),         # steering arm / toe-link pickup
    }
    body = {
        f"{p}a1{s}": (sx * 0.32, y0 - 0.22, 0.20),                # lower arm, front pivot
        f"{p}a2{s}": (sx * 0.32, y0 + 0.22, 0.20),                # lower arm, rear pivot
        f"{p}u1{s}": (sx * 0.44, y0 - 0.13, 0.60),                # upper link pivots
        f"{p}u2{s}": (sx * 0.44, y0 + 0.15, 0.60),
        f"{p}s1{s}": (sx * (tr - 0.22), y0 + 0.02, 0.80),         # spring / damper top mount
        f"{p}x1{s}": (sx * 0.28, y0 + 0.16, 0.26),                # steering rack end / toe link pivot
    }
    return k, body


def body_anchor_nodes(axle, s):
    i = 2 if axle == "f" else 7
    j = 1 if axle == "f" else 8
    m = 3 if axle == "f" else 6
    o = "r" if s == "l" else "l"
    return [lo(i, s), mid(i, s), lo(j, s), mid(j, s), lo(m, s), lo(i, o)]


def suspension_part(axle, key, title, spring, damp, ride, info_extra):
    """Front (axle='f') or rear (axle='r') suspension variant."""
    A = axle.upper()
    load = LOAD_F if axle == "f" else LOAD_R
    nodes = [["id", "posX", "posY", "posZ"], {"nodeMaterial": "|NM_METAL"}, {"frictionCoef": 0.5},
             {"collision": True}, {"selfCollision": False}]
    beams = [["id1:", "id2:"], {"beamPrecompression": 1, "beamType": "|NORMAL", "beamLongBound": 1, "beamShortBound": 1}]
    hub_beams, arm_beams, mount_beams, springs = [], [], [], []
    spring_len = None
    for sx in (1, -1):
        s = S(sx)
        k, body = corner(axle, sx)
        nodes += [{"group": [f"laguna2_suspension_{A}", f"wheelhub_{A}{s.upper()}"]}, {"nodeWeight": 6}]
        nodes += [[n, round(x, 3), round(y, 3), round(z, 3)] for n, (x, y, z) in k.items()]
        nodes += [{"group": ["laguna2_body", f"laguna2_suspension_{A}"]}, {"nodeWeight": 3}]
        nodes += [[n, round(x, 3), round(y, 3), round(z, 3)] for n, (x, y, z) in body.items()]
        kn = list(k)
        hub_beams += [[kn[a], kn[b]] for a in range(len(kn)) for b in range(a + 1, len(kn))]
        p = axle
        arm_beams += [[f"{p}a1{s}", f"{p}h1{s}"], [f"{p}a2{s}", f"{p}h1{s}"],
                      [f"{p}u1{s}", f"{p}h2{s}"], [f"{p}u2{s}", f"{p}h2{s}"]]
        if axle == "r":
            arm_beams.append([f"{p}x1{s}", f"{p}k1{s}"])            # rear toe link (fixed)
        for bn in body:
            for an in body_anchor_nodes(axle, s):
                mount_beams.append([bn, an])
        springs.append([f"{p}s1{s}", f"{p}h1{s}"])
        a, b = body[f"{p}s1{s}"], k[f"{p}h1{s}"]
        spring_len = math.dist(a, b)
    nodes.append({"group": ""})
    beams += [{"beamSpring": 12000000, "beamDamp": 300}, {"beamDeform": "FLT_MAX", "beamStrength": "FLT_MAX"}] + hub_beams
    beams += [{"beamSpring": 9000000, "beamDamp": 250}, {"beamDeform": 120000, "beamStrength": 300000}] + arm_beams
    beams += [{"beamSpring": 6000000, "beamDamp": 200}, {"beamDeform": 150000, "beamStrength": "FLT_MAX"}] + mount_beams
    # Coil-over: preload so the static corner load sits at design height (+ ride offset).
    beams += [{"beamType": "|NORMAL"},
              {"beamSpring": f"$spring_{A}", "beamDamp": f"$damp_{A}"},
              {"beamDeform": "FLT_MAX", "beamStrength": "FLT_MAX"},
              {"beamPrecompression": f"$=1 + ({load:.0f} / $spring_{A} + $ride_{A}) / {spring_len:.4f}"}]
    beams += springs
    beams += [{"beamPrecompression": 1, "beamSpring": 0, "beamDamp": 0}]
    variables = [["name", "type", "unit", "category", "default", "min", "max", "title", "description"],
                 [f"$spring_{A}", "range", "N/m", "Suspension", spring, 15000, 90000, f"{'Front' if axle == 'f' else 'Rear'} Spring Rate",
                  "Spring stiffness at the wheel"],
                 [f"$damp_{A}", "range", "N/m/s", "Suspension", damp, 1000, 8000, f"{'Front' if axle == 'f' else 'Rear'} Damping",
                  "Damper strength"],
                 [f"$ride_{A}", "range", "m", "Suspension", ride, -0.06, 0.05, f"{'Front' if axle == 'f' else 'Rear'} Ride Height",
                  "Raises (+) or lowers (-) the body at this axle"]]
    part = {
        "information": {"authors": AUTHORS, "name": title, **info_extra},
        "slotType": f"laguna2_suspension_{A}",
        "variables": variables,
        "nodes": nodes,
        "beams": beams,
    }
    if axle == "f":
        part["hydros"] = [["id1:", "id2:"],
                          {"beamSpring": 3000000, "beamDamp": 150},
                          {"inputSource": "steering", "inputFactor": 1, "inRate": 2.2, "outRate": 2.2},
                          {"steeringWheelLock": 470},
                          ["fx1l", "fk1l", {"factor": 0.22}],
                          ["fx1r", "fk1r", {"factor": -0.22}]]
    return key, part


def suspensions():
    parts = {}
    specs = [
        ("standard", "Standard", (34000, 2600, 0.0), (28000, 2300, 0.0), {"value": 0}),
        ("sport", "Sport (GT, firmer and 15 mm lower)", (44000, 3400, -0.015), (36000, 3000, -0.015), {"value": 450}),
        ("lowered", "Lowered (aftermarket, 40 mm)", (58000, 4200, -0.04), (48000, 3800, -0.04), {"value": 600}),
    ]
    for key, title, f, r, info in specs:
        k, p = suspension_part("f", f"laguna2_suspension_F_{key}", f"Front Suspension: MacPherson, {title}", *f, info)
        parts[k] = p
        k, p = suspension_part("r", f"laguna2_suspension_R_{key}", f"Rear Suspension: Torsion Beam, {title}", *r, info)
        parts[k] = p
    for key, title, f_t, r_t, info in (("standard", "Standard brakes (vented front discs)", 1700, 800, {"value": 0}),
                                       ("large", "Large brakes (V6 / 2.0T / GT)", 2300, 1000, {"value": 380})):
        parts[f"laguna2_brakes_{key}"] = {
            "information": {"authors": AUTHORS, "name": title, **info},
            "slotType": "laguna2_brakes",
            "variables": [["name", "type", "unit", "category", "default", "min", "max", "title", "description"],
                          ["$brake_F", "range", "N*m", "Brakes", f_t, 800, 3500, "Front Brake Torque", ""],
                          ["$brake_R", "range", "N*m", "Brakes", r_t, 400, 2000, "Rear Brake Torque", ""],
                          ["$parking_R", "range", "N*m", "Brakes", 1500, 500, 3000, "Handbrake Torque", ""]],
        }
    return parts


# --------------------------------------------------------------------------
# Wheels
# --------------------------------------------------------------------------
TYRE_COMMON = [
    {"hasTire": True}, {"enableTireReinfBeams": True}, {"enableTireLbeams": True},
    {"enableTireSideReinfBeams": True}, {"enableTreadReinfBeams": True}, {"enableTirePeripheryReinfBeams": True},
    {"numRays": 16},
    {"nodeMaterial": "|NM_RUBBER"}, {"hubNodeMaterial": "|NM_METAL"},
    {"frictionCoef": 1.0}, {"slidingFrictionCoef": 0.72},
    {"noLoadCoef": 1.55}, {"fullLoadCoef": 0.5}, {"loadSensitivitySlope": 0.00018},
    {"softnessCoef": 0.6}, {"treadCoef": 1.0},
    {"pressurePSI": 32}, {"maxPressure": 60},
    {"wheelSideBeamSpring": 60000}, {"wheelSideBeamDamp": 20},
    {"wheelTreadBeamSpring": 450000}, {"wheelTreadBeamDamp": 20},
    {"wheelPeripheryBeamSpring": 1200000}, {"wheelPeripheryBeamDamp": 30},
    {"wheelReinfBeamSpring": 1200}, {"wheelReinfBeamDamp": 15},
    {"wheelSideReinfBeamSpring": 6000}, {"wheelSideReinfBeamDamp": 8},
    {"wheelTreadReinfBeamSpring": 6000}, {"wheelTreadReinfBeamDamp": 8},
    {"wheelPeripheryReinfBeamSpring": 30000}, {"wheelPeripheryReinfBeamDamp": 20},
    {"wheelHubBeamSpring": 12000000}, {"wheelHubBeamDamp": 200},
    {"wheelHubBeamDeform": "FLT_MAX"}, {"wheelHubBeamStrength": "FLT_MAX"},
    {"dragCoef": 5}, {"speedo": True},
]


def wheel_part(key, title, mesh, radius, width, hub_r, node_w, hub_w, value):
    pw = [["name", "hubGroup", "group", "node1:", "node2:", "nodeS", "nodeArm:", "wheelDir"]]
    pw += [{"radius": radius}, {"tireWidth": width}, {"hubRadius": hub_r}, {"hubWidth": width * 0.85},
           {"nodeWeight": node_w}, {"hubNodeWeight": hub_w}] + TYRE_COMMON
    flex = [["mesh", "[group]:", "nonFlexMaterials"]]
    for axle, A, y, tr in (("f", "F", Y_AXLE_F, TRACK_F), ("r", "R", Y_AXLE_R, TRACK_R)):
        if axle == "f":
            pw += [{"brakeTorque": "$brake_F"}, {"parkingTorque": 0}]
        else:
            pw += [{"brakeTorque": "$brake_R"}, {"parkingTorque": "$parking_R"}]
        for sx, s, wdir in ((1, "l", -1), (-1, "r", 1)):
            name = f"{A}{s.upper()}"
            pw.append([name, f"wheelhub_{name}", f"wheel_{name}", f"{axle}w1{s}", f"{axle}w2{s}", 9999, f"{axle}h2{s}", wdir])
            flex.append([mesh, [f"wheel_{name}", f"wheelhub_{name}"], [],
                         {"pos": {"x": round(sx * tr, 3), "y": round(y, 3), "z": WHEEL_R},
                          "rot": {"x": 0, "y": 0, "z": 0 if sx > 0 else 180},
                          "scale": {"x": 1, "y": 1, "z": 1}}])
    return key, {
        "information": {"authors": AUTHORS, "name": title, "value": value},
        "slotType": "laguna2_wheels",
        "pressureWheels": pw,
        "flexbodies": flex,
    }


def wheels():
    return dict([
        wheel_part("laguna2_wheels_alloy17", "17\" Ten-Spoke Alloys, 225/45 R17", "laguna2_wheel_alloy17",
                   0.317, 0.225, 0.22, 0.30, 1.1, 900),
        wheel_part("laguna2_wheels_steel15", "15\" Steel Wheels with Renault Hubcaps, 195/65 R15", "laguna2_wheel_steel15",
                   0.3175, 0.195, 0.19, 0.26, 1.3, 0),
    ])


# --------------------------------------------------------------------------
# Engines and transmissions (real Laguna II range)
# --------------------------------------------------------------------------
# key: (name, code, fuel, idle, maxrpm, torque curve [(rpm, Nm)], inertia, friction, weight bias, gearbox family, default gearbox, value)
ENGINES = {
    "16": ("1.6 16V", "K4M", "gasoline", 750, 6500,
           [(0, 0), (1000, 105), (2000, 128), (3000, 140), (4200, 151), (5000, 147), (6000, 132), (6500, 116), (7000, 90)],
           0.11, 11, "A", "5M", 0),
    "18": ("1.8 16V", "F4P", "gasoline", 750, 6500,
           [(0, 0), (1000, 118), (2000, 148), (3000, 165), (3750, 173), (5000, 165), (5750, 149), (6500, 120), (7000, 95)],
           0.12, 12, "B", "5M", 600),
    "20": ("2.0 16V", "F4R", "gasoline", 750, 6500,
           [(0, 0), (1000, 130), (2000, 165), (3000, 182), (3750, 191), (5000, 185), (5500, 175), (6000, 160), (6500, 140), (7000, 110)],
           0.13, 13, "C", "5M", 1200),
    "20t": ("2.0 16V Turbo", "F4Rt", "gasoline", 800, 6300,
            [(0, 0), (1000, 150), (1500, 205), (2000, 250), (3250, 270), (4500, 262), (5000, 240), (5500, 220), (6000, 195), (6500, 160)],
            0.14, 14, "D", "6M", 2800),
    "v6": ("3.0 V6 24V", "L7X", "gasoline", 700, 6500,
           [(0, 0), (1000, 200), (2000, 245), (3000, 270), (3750, 285), (5000, 275), (6000, 245), (6500, 215), (7000, 170)],
           0.18, 15, "E", "5A", 4200),
    "19dci": ("1.9 dCi", "F9Q", "diesel", 800, 4600,
              [(0, 0), (1000, 170), (1500, 240), (2000, 300), (2500, 295), (3000, 275), (4000, 215), (4500, 170), (5000, 100)],
              0.17, 16, "F", "6M", 1500),
    "22dci": ("2.2 dCi", "G9T", "diesel", 800, 4500,
              [(0, 0), (1000, 190), (1500, 280), (1750, 320), (2500, 320), (3000, 305), (4000, 260), (4500, 200), (5000, 120)],
              0.19, 17, "D", "6M", 2400),
    "20dci": ("2.0 dCi", "M9R", "diesel", 800, 4700,
              [(0, 0), (1000, 200), (1500, 290), (2000, 340), (2750, 340), (3250, 320), (4000, 275), (4500, 220), (5000, 140)],
              0.18, 16, "D", "6M", 3000),
}
# gearbox key: (name, kind, ratios (rev first, then forward), final drive, value)
GEARBOXES = {
    "5M": ("5-Speed Manual (JR5)", "manual", [-3.55, 0, 3.73, 2.05, 1.39, 1.03, 0.76], 4.21, 0),
    "6M": ("6-Speed Manual (PK6)", "manual", [-3.55, 0, 3.73, 2.05, 1.39, 1.03, 0.82, 0.69], 3.87, 350),
    "4A": ("4-Speed Automatic \"Proactive\" (DP0)", "auto", [-2.46, 0, 2.72, 1.50, 1.00, 0.71], 4.12, 900),
    "5A": ("5-Speed Automatic with +/- mode (Aisin AJ0)", "auto", [-3.37, 0, 3.52, 2.04, 1.40, 1.00, 0.73], 3.65, 1300),
}
# gearbox families (which gearboxes fit which engine), from the real range
FAMILIES = {"A": ["5M"], "B": ["5M", "4A"], "C": ["5M", "6M", "4A"], "D": ["6M", "5A"], "E": ["5A", "6M"],
            "F": ["5M", "6M", "5A"]}


def kw_hp(curve, rpm_max):
    best = max(t * r for r, t in curve if r <= rpm_max + 500) * 2 * math.pi / 60 / 1000
    return round(best), round(best * 1.341)


def engines():
    parts = {}
    for key, (name, code, fuel, idle, maxrpm, curve, inertia, friction, fam, gb_default, value) in ENGINES.items():
        kw, hp = kw_hp(curve, maxrpm)
        diesel = fuel == "diesel"
        parts[f"laguna2_engine_{key}"] = {
            "information": {"authors": AUTHORS, "name": f"{name} ({code}), {hp} hp", "value": value},
            "slotType": "laguna2_engine",
            "slots": [["type", "default", "description"],
                      [f"laguna2_transmission_{fam}", f"laguna2_transmission_{gb_default}_{fam}", "Transmission"]],
            "variables": [["name", "type", "unit", "category", "default", "min", "max", "title", "description"],
                          ["$fuel", "range", "L", "Chassis", 40, 0, 68, "Starting Fuel", "Litres in the 68 L tank"]],
            "powertrain": [["type", "name", "inputName", "inputIndex"],
                           ["combustionEngine", "mainEngine", "dummy", 0]],
            "energyStorage": [["type", "name"], ["fuelTank", "mainTank"]],
            "mainTank": {"energyType": fuel, "fuelCapacity": 68, "startingFuelCapacity": "$fuel"},
            "mainEngine": {
                "torque": [["rpm", "torque"]] + [[r, t] for r, t in curve],
                "idleRPM": idle,
                "maxRPM": maxrpm,
                "revLimiterRPM": maxrpm,
                "hasRevLimiter": True,
                "inertia": inertia,
                "friction": friction,
                "dynamicFriction": 0.028 if diesel else 0.024,
                "engineBrakeTorque": 45 if diesel else 38,
                "burnEfficiency": 0.40 if diesel else 0.33,
                "requiredEnergyType": fuel,
                "energyStorage": "mainTank",
                "torqueReactionNodes:": ["e1l", "e2l", "e1r"],
                "particulates": 0.08 if diesel else 0.02,
                "starterTorque": 120,
            },
        }
    trans = {}
    for fam, keys in FAMILIES.items():
        for gk in keys:
            name, kind, ratios, final, value = GEARBOXES[gk]
            if kind == "manual":
                pt = [["type", "name", "inputName", "inputIndex"],
                      ["frictionClutch", "clutch", "mainEngine", 1],
                      ["manualGearbox", "gearbox", "clutch", 1]]
                extra = {"gearbox": {"gearRatios": ratios, "friction": 1.2, "dynamicFriction": 0.0004},
                         "clutch": {"clutchFreePlay": 0.75, "lockSpringCoef": 0.3}}
            else:
                pt = [["type", "name", "inputName", "inputIndex"],
                      ["torqueConverter", "torqueConverter", "mainEngine", 1],
                      ["automaticGearbox", "gearbox", "torqueConverter", 1]]
                extra = {"gearbox": {"gearRatios": ratios, "parkLockTorque": 2500, "friction": 1.6, "dynamicFriction": 0.0006},
                         "torqueConverter": {"converterDiameter": 0.25, "converterStiffness": 10, "couplingAVRatio": 0.9,
                                             "stallTorqueRatio": 2.0, "lockupClutchTorque": 450}}
            trans[f"laguna2_transmission_{gk}_{fam}"] = {
                "information": {"authors": AUTHORS, "name": name, "value": value},
                "slotType": f"laguna2_transmission_{fam}",
                "slots": [["type", "default", "description"],
                          ["laguna2_differential", "laguna2_differential_open", "Front Differential"]],
                "variables": [["name", "type", "unit", "category", "default", "min", "max", "title", "description"],
                              ["$finaldrive", "range", ":1", "Differentials", final, 2.5, 6.0, "Final Drive Ratio",
                               "Higher = quicker acceleration, lower top speed"]],
                "powertrain": pt,
                **extra,
            }
    for key, title, props, value in (
            ("open", "Open Differential (factory)", {"diffType": "open"}, 0),
            ("lsd", "Limited-Slip Differential (aftermarket)", {"diffType": "lsd", "lsdPreload": 60, "lsdLockCoef": 0.18,
                                                                 "lsdRevLockCoef": 0.10}, 650)):
        trans[f"laguna2_differential_{key}"] = {
            "information": {"authors": AUTHORS, "name": title, "value": value},
            "slotType": "laguna2_differential",
            "powertrain": [["type", "name", "inputName", "inputIndex"],
                           ["differential", "differential_F", "gearbox", 1, {"gearRatio": "$finaldrive", "friction": 2.5, **props}],
                           ["shaft", "wheelaxleFL", "differential_F", 1, {"connectedWheel": "FL"}],
                           ["shaft", "wheelaxleFR", "differential_F", 2, {"connectedWheel": "FR"}]],
        }
    return parts, trans


# --------------------------------------------------------------------------
# Body and exterior options
# --------------------------------------------------------------------------
import sys  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "tools", "laguna2"))
import lights  # noqa: E402

FLEX = ["mesh", "[group]:", "nonFlexMaterials"]


def flex(*meshes):
    return [FLEX] + [[m, ["laguna2_body"]] for m in meshes]


def option(slot, key, title, meshes, value=0, glow=None, glow_variant=None, extra=None):
    p = {"information": {"authors": AUTHORS, "name": title, "value": value}, "slotType": slot}
    if meshes:
        p["flexbodies"] = flex(*meshes)
    if glow:
        p["glowMap"] = lights.glow_map(glow, glow_variant)
    if extra:
        p.update(extra)
    return key, p


HEAD = ["laguna2_hl_low", "laguna2_hl_low_lens", "laguna2_hl_position", "laguna2_hl_high",
        "laguna2_hl_signal_L", "laguna2_hl_signal_R"]
TAIL = ["laguna2_tail_lens_red", "laguna2_tail_reflector", "laguna2_tail_eye_red", "laguna2_tail_fog",
        "laguna2_reverse", "laguna2_tail_signal_L", "laguna2_tail_signal_R"]

# slot: (description, default part, [options])
EXTERIOR = {
    "laguna2_headlights": ("Headlights", "laguna2_headlights_halogen", [
        option("laguna2_headlights", "laguna2_headlights_halogen", "Headlights: Halogen (factory)", ["laguna2_headlights"],
               glow=HEAD),
        option("laguna2_headlights", "laguna2_headlights_xenon", "Headlights: Xenon (high trims)", ["laguna2_headlights"],
               value=700, glow=HEAD, glow_variant={m: "_xenon" for m in lights.XENON}),
    ]),
    "laguna2_taillights": ("Tail Lights", "laguna2_taillights_factory", [
        option("laguna2_taillights", "laguna2_taillights_factory", "Tail Lights: Factory", ["laguna2_taillights"], glow=TAIL),
        option("laguna2_taillights", "laguna2_taillights_smoked", "Tail Lights: Smoked (aftermarket)",
               ["laguna2_taillights_smoked"], value=180,
               glow=["laguna2_tail_lens_smoked"] + TAIL[1:]),
    ]),
    "laguna2_foglights": ("Front Fog Lights", "laguna2_foglights_round", [
        option("laguna2_foglights", "laguna2_foglights_round", "Front Fog Lights: Round (bumper)", ["laguna2_foglights"],
               value=150, glow=["laguna2_fog"]),
    ]),
    "laguna2_glass": ("Side & Rear Glass", "laguna2_glass_factory", [
        option("laguna2_glass", "laguna2_glass_factory", "Glass: Factory light tint", ["laguna2_glass_factory"]),
        option("laguna2_glass", "laguna2_glass_privacy", "Glass: Privacy (darker rear)", ["laguna2_glass_privacy"], value=250),
        option("laguna2_glass", "laguna2_glass_dark", "Glass: Dark film (aftermarket)", ["laguna2_glass_dark"], value=120),
    ]),
    "laguna2_mirrors": ("Side Mirrors", "laguna2_mirrors_body", [
        option("laguna2_mirrors", "laguna2_mirrors_body", "Side Mirrors: Body-coloured caps", ["laguna2_mirrors"]),
    ]),
    "laguna2_rearwiper": ("Rear Wiper", "laguna2_rearwiper", [
        option("laguna2_rearwiper", "laguna2_rearwiper", "Rear Wiper", ["laguna2_rearwiper"]),
    ]),
    "laguna2_mouldings": ("Side Mouldings", "laguna2_mouldings_black", [
        option("laguna2_mouldings", "laguna2_mouldings_black", "Side Mouldings: Black", ["laguna2_mouldings_black"]),
        option("laguna2_mouldings", "laguna2_mouldings_body", "Side Mouldings: Body-coloured", ["laguna2_mouldings_body"],
               value=90),
    ]),
    "laguna2_parksensors": ("Rear Parking Sensors", "", [
        option("laguna2_parksensors", "laguna2_parksensors", "Rear Parking Sensors", ["laguna2_parksensors"], value=300),
    ]),
    "laguna2_plate_F": ("Front License Plate", "laguna2_plate_F_eu", [
        option("laguna2_plate_F", "laguna2_plate_F_eu", "Front Plate: EU (France)", ["laguna2_plate_F"]),
    ]),
    "laguna2_plate_R": ("Rear License Plate", "laguna2_plate_R_eu", [
        option("laguna2_plate_R", "laguna2_plate_R_eu", "Rear Plate: EU (France)", ["laguna2_plate_R"]),
    ]),
    "laguna2_badges": ("Rear Badges", "laguna2_badges_laguna", [
        option("laguna2_badges", "laguna2_badges_laguna", "\"LAGUNA\" Script", ["laguna2_lettering"]),
    ]),
}


def body_part():
    slots = [["type", "default", "description"],
             ["laguna2_engine", "laguna2_engine_19dci", "Engine"],
             ["laguna2_suspension_F", "laguna2_suspension_F_standard", "Front Suspension"],
             ["laguna2_suspension_R", "laguna2_suspension_R_standard", "Rear Suspension"],
             ["laguna2_brakes", "laguna2_brakes_standard", "Brakes"],
             ["laguna2_wheels", "laguna2_wheels_alloy17", "Wheels & Tyres"]]
    for slot, (desc, default, _opts) in EXTERIOR.items():
        slots.append([slot, default, desc])
    return {
        "information": {"authors": AUTHORS, "name": "Laguna II Liftback (5-door)", "value": 9000},
        "slotType": "laguna2_body",
        "slots": slots,
        "refNodes": [["ref:", "back:", "left:", "up:"], [lo(4, "r"), lo(5, "r"), lo(4, "l"), mid(4, "r")]],
        "cameraExternal": {"distance": 5.8, "distanceMin": 3, "offset": {"x": 0, "y": 0.2, "z": 0.62}, "fov": 65},
        "nodes": chassis_nodes(),
        "beams": chassis_beams(),
        "triangles": chassis_triangles(),
        "flexbodies": flex("laguna2_body", "laguna2_hood", "laguna2_bumper_F", "laguna2_bumper_R", "laguna2_tailgate",
                           "laguna2_windscreen", "laguna2_interior"),
        "glowMap": lights.glow_map(["laguna2_repeater_L", "laguna2_repeater_R", "laguna2_brake3", "laguna2_platelight"]),
    }


# --------------------------------------------------------------------------
# Paints and configurations
# --------------------------------------------------------------------------
def paint(r, g, b, metallic=0.6, rough=0.32, coat=0.85, coat_rough=0.05):
    return {"baseColor": [r, g, b, 1.0], "metallic": metallic, "roughness": rough,
            "clearcoat": coat, "clearcoatRoughness": coat_rough}


# Laguna II era Renault colours (names as sold in France; values approximate).
PAINTS = {
    "Gris Hologramme": paint(0.55, 0.57, 0.60),
    "Gris Eclipse": paint(0.20, 0.21, 0.23),
    "Gris Platine": paint(0.66, 0.67, 0.68),
    "Noir Nacre": paint(0.025, 0.025, 0.03, 0.4, 0.25),
    "Blanc Glacier": paint(0.86, 0.87, 0.87, 0.0, 0.4, 0.6),
    "Rouge de Feu": paint(0.50, 0.03, 0.04, 0.5, 0.3),
    "Rouge Vif": paint(0.62, 0.02, 0.02, 0.0, 0.38, 0.6),
    "Bleu Iliade": paint(0.03, 0.10, 0.36),
    "Bleu Nuit": paint(0.03, 0.05, 0.14),
    "Vert Fougere": paint(0.07, 0.17, 0.12),
    "Beige Champagne": paint(0.62, 0.55, 0.42),
}

CONFIGS = {
    "laguna2_authentique_16": dict(
        title="Authentique 1.6 16V", desc="Entry model: 1.6 petrol, 5-speed, steel wheels, no fog lights.",
        engine="16", gearbox="5M", paint="Blanc Glacier", value=17500, years=(2001, 2005),
        parts={"laguna2_wheels": "laguna2_wheels_steel15", "laguna2_foglights": ""}),
    "laguna2_expression_19dci": dict(
        title="Expression 1.9 dCi", desc="The everyday Laguna: 1.9 dCi diesel, 6-speed manual, alloys.",
        engine="19dci", gearbox="6M", paint="Gris Hologramme", value=21500, years=(2001, 2005), parts={}),
    "laguna2_privilege_22dci": dict(
        title="Privilege 2.2 dCi Auto", desc="Comfortable diesel cruiser: 2.2 dCi, 5-speed automatic, xenon lights, privacy glass, parking sensors.",
        engine="22dci", gearbox="5A", paint="Bleu Iliade", value=27500, years=(2001, 2005),
        parts={"laguna2_headlights": "laguna2_headlights_xenon", "laguna2_glass": "laguna2_glass_privacy",
               "laguna2_parksensors": "laguna2_parksensors", "laguna2_mouldings": "laguna2_mouldings_body"}),
    "laguna2_dynamique_20t": dict(
        title="Dynamique 2.0 16V Turbo", desc="The quick one: 2.0 turbo, 6-speed, sport suspension and larger brakes.",
        engine="20t", gearbox="6M", paint="Rouge de Feu", value=26000, years=(2001, 2005),
        parts={"laguna2_suspension_F": "laguna2_suspension_F_sport", "laguna2_suspension_R": "laguna2_suspension_R_sport",
               "laguna2_brakes": "laguna2_brakes_large", "laguna2_headlights": "laguna2_headlights_xenon",
               "laguna2_mouldings": "laguna2_mouldings_body"}),
    "laguna2_initiale_v6": dict(
        title="Initiale 3.0 V6 Auto", desc="Top of the range: 3.0 V6, 5-speed automatic, xenon, privacy glass, every option.",
        engine="v6", gearbox="5A", paint="Noir Nacre", value=34500, years=(2001, 2005),
        parts={"laguna2_brakes": "laguna2_brakes_large", "laguna2_headlights": "laguna2_headlights_xenon",
               "laguna2_glass": "laguna2_glass_privacy", "laguna2_parksensors": "laguna2_parksensors",
               "laguna2_mouldings": "laguna2_mouldings_body"}),
    "laguna2_tuned_20t": dict(
        title="2.0 Turbo Street (aftermarket)", desc="Lowered, LSD, smoked tail lights and dark windows: a modified 2.0 turbo.",
        engine="20t", gearbox="6M", paint="Gris Eclipse", value=24000, years=(2001, 2005), config_type="Custom",
        parts={"laguna2_suspension_F": "laguna2_suspension_F_lowered", "laguna2_suspension_R": "laguna2_suspension_R_lowered",
               "laguna2_brakes": "laguna2_brakes_large", "laguna2_taillights": "laguna2_taillights_smoked",
               "laguna2_glass": "laguna2_glass_dark", "laguna2_rearwiper": "", "laguna2_differential": "laguna2_differential_lsd",
               "laguna2_mouldings": "laguna2_mouldings_body"}),
}
DEFAULT_CONFIG = "laguna2_expression_19dci"


def config_files(engine_parts):
    out = {}
    for key, c in CONFIGS.items():
        fam = ENGINES[c["engine"]][8]
        parts = {
            "laguna2_body": "laguna2_body_liftback",
            "laguna2_engine": f"laguna2_engine_{c['engine']}",
            f"laguna2_transmission_{fam}": f"laguna2_transmission_{c['gearbox']}_{fam}",
        }
        parts.update(c["parts"])
        pc = {"format": 2, "model": MODEL, "parts": parts, "vars": {},
              "paints": [PAINTS[c["paint"]]] * 3}
        name, code, fuel, _i, maxrpm, curve = ENGINES[c["engine"]][:6]
        kw, hp = kw_hp(curve, maxrpm)
        gb = GEARBOXES[c["gearbox"]]
        info = {
            "Configuration": c["title"],
            "Description": c["desc"],
            "Config Type": c.get("config_type", "Factory"),
            "Value": c["value"],
            "Body Style": "Liftback",
            "Drivetrain": "FWD",
            "Fuel Type": "Diesel" if fuel == "diesel" else "Gasoline",
            "Induction Type": "Turbo" if c["engine"] in ("20t", "19dci", "22dci", "20dci") else "NA",
            "Transmission": "Automatic" if gb[1] == "auto" else "Manual",
            "Power": hp,
            "Torque": max(t for _r, t in curve),
            "Weight": 1305,
            "Years": {"min": c["years"][0], "max": c["years"][1]},
            "defaultPaintName1": c["paint"],
        }
        out[key] = (pc, info)
    return out


# --------------------------------------------------------------------------
def write_jbeam(name, parts):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(parts, fh, indent=2)
        fh.write("\n")
    print(f"[gen] {name}: {len(parts)} parts")


def main():
    for old in ("laguna_body.jbeam", "laguna_physics.jbeam", "laguna_engines.jbeam", "laguna_transmissions.jbeam",
                "laguna_suspension.jbeam", ".mesh_index.json"):
        p = os.path.join(OUT, old)
        if os.path.exists(p):
            os.remove(p)
            print(f"[gen] removed old {old}")

    write_jbeam("renault_laguna.jbeam", {MODEL: {
        "information": {"authors": AUTHORS, "name": "Renault Laguna II (X74)", "value": 0},
        "slotType": "main",
        "slots": [["type", "default", "description"],
                  ["laguna2_body", "laguna2_body_liftback", "Body Style"],
                  ["paint_design", "", "Paint Design"]],
        "controller": [["fileName"], ["vehicleController", {}]],
        "scalenodes": {"nodeOffset": {"x": 0.0, "y": 0.0, "z": 0.0}},
    }})
    write_jbeam("laguna2_body.jbeam", {"laguna2_body_liftback": body_part()})
    write_jbeam("laguna2_suspension.jbeam", suspensions())
    write_jbeam("laguna2_wheels.jbeam", wheels())
    eng, trans = engines()
    write_jbeam("laguna2_engines.jbeam", eng)
    write_jbeam("laguna2_transmissions.jbeam", trans)
    ext = {}
    for slot, (_d, _default, opts) in EXTERIOR.items():
        ext.update(dict(opts))
    write_jbeam("laguna2_exterior.jbeam", ext)

    for f in os.listdir(OUT):
        if f.endswith(".pc") or (f.startswith("info_") and f.endswith(".json")):
            os.remove(os.path.join(OUT, f))
    for key, (pc, info) in config_files(eng).items():
        with open(os.path.join(OUT, key + ".pc"), "w", encoding="utf-8") as fh:
            json.dump(pc, fh, indent=2)
        with open(os.path.join(OUT, f"info_{key}.json"), "w", encoding="utf-8") as fh:
            json.dump(info, fh, indent=2)
    print(f"[gen] {len(CONFIGS)} configurations")

    info = {
        "Name": "Laguna II",
        "Brand": "Renault",
        "Author": AUTHORS,
        "Type": "Car",
        "Body Style": "Liftback",
        "Country": "France",
        "Derby Class": "Compact",
        "Years": {"min": 2001, "max": 2007},
        "default_pc": DEFAULT_CONFIG,
        "default_color": "Gris Hologramme",
        "paints": PAINTS,
    }
    with open(os.path.join(OUT, "info.json"), "w", encoding="utf-8") as fh:
        json.dump(info, fh, indent=2)
    print("[gen] info.json")


if __name__ == "__main__":
    main()
