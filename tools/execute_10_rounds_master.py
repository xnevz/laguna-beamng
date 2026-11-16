"""
execute_10_rounds_master.py
===========================
Executes a 10-round systematic refinement pass on the Renault Laguna II Phase 1 (2001-2005)
in Blender 5.3:
  Round 1: Non-shiny, semi-matte Champagne Silver (Beige Poivre) paint calibration.
  Round 2: Eradicate race remnants (roll cage, fuel cell) poking through decklid & fill bumper hole.
  Round 3: Add front and rear continuous protective bumper rub strips.
  Round 4: Re-engineer authentic Renault 7-spoke silver wheel covers & civilian tire sidewalls.
  Round 5: Headlight overhaul with flush clear lens, dual chrome projectors, and amber corners.
  Round 6: Refine front nose beak, split grille horizontal slats, and lower fog lights.
  Round 7: Park front wipers properly in cowl tray and align rear liftback wiper flush to glass.
  Round 8: Two-tone ruby/clear taillight refinement and high-mounted 3rd brake light.
  Round 9: Factory pale green Solarglass tint, matte black pillars, and visible cockpit depth.
  Round 10: Tailgate chrome diamond & badges, European license plate, calibrated daylight & 1080p renders.
"""

import bpy
import mathutils
import math
import os
import shutil

PROJECT_ROOT = r"C:\Users\abdelkarim\Documents\laguna-beamng"
ARTIFACT_DIR = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"

def get_or_create_mat(name):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    return m

def execute_10_rounds():
    print("==========================================================")
    print("STARTING 10-ROUND COMPREHENSIVE VISUAL REFINEMENT PASS")
    print("==========================================================")
    scene = bpy.context.scene

    # --------------------------------------------------------
    # ROUND 1: SEMI-MATTE BEIGE POIVRE PAINT CALIBRATION
    # --------------------------------------------------------
    print("[Round 1] Calibrating authentic Beige Poivre semi-matte finish...")
    mat_paint = get_or_create_mat("Laguna_Champagne_Silver")
    mat_paint.use_nodes = True
    bsdf = mat_paint.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        # Authentic Renault Beige Poivre (B64): warm champagne grey/taupe
        # Linear sRGB values tuned to prevent overexposure:
        bsdf.inputs['Base Color'].default_value = (0.44, 0.40, 0.34, 1.0)
        # Reduced metallic tone for civilian semi-matte feel
        bsdf.inputs['Metallic'].default_value = 0.12
        # Increased roughness for non-shiny, satin automotive sheen
        bsdf.inputs['Roughness'].default_value = 0.44
        bsdf.inputs['IOR'].default_value = 1.50
        # Gentle clearcoat without mirror glare
        bsdf.inputs['Coat Weight'].default_value = 0.15
        bsdf.inputs['Coat Roughness'].default_value = 0.30
        if 'Specular IOR Level' in bsdf.inputs:
            bsdf.inputs['Specular IOR Level'].default_value = 0.45

    # Secondary paint alias
    mat_paint2 = bpy.data.materials.get("Laguna_Paint_BeigePoivre")
    if mat_paint2 and mat_paint2.node_tree:
        bsdf2 = mat_paint2.node_tree.nodes.get("Principled BSDF")
        if bsdf2:
            bsdf2.inputs['Base Color'].default_value = (0.44, 0.40, 0.34, 1.0)
            bsdf2.inputs['Metallic'].default_value = 0.12
            bsdf2.inputs['Roughness'].default_value = 0.44
            bsdf2.inputs['Coat Weight'].default_value = 0.15
            bsdf2.inputs['Coat Roughness'].default_value = 0.30

    # --------------------------------------------------------
    # ROUND 2: ERADICATE RACE REMNANTS & CLEAN REAR DECKLID
    # --------------------------------------------------------
    print("[Round 2] Eradicating race cage remnants & cleaning rear decklid...")
    # Hide racing interior equipment that poked through rear decklid
    race_remnants = [
        'unnamed.030', 'unnamed.149', 'unnamed.150', 'unnamed.152', 'unnamed.155',
        'unnamed.159', 'unnamed.161', 'unnamed.190', 'unnamed.213', 'unnamed.214',
        'unnamed.216', 'unnamed.219', 'unnamed.069' # 069 is right headlight blanking plate
    ]
    for n in race_remnants:
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = True
            o.hide_viewport = True

    # Ensure trunk lid meshes have paint assigned
    for deck_name in ['unnamed.025', 'unnamed.026', 'unnamed.028']:
        o = bpy.data.objects.get(deck_name)
        if o:
            o.hide_render = False
            o.hide_viewport = False
            o.data.materials.clear()
            o.data.materials.append(mat_paint)

    # Plug the circular racing hole on right rear bumper
    old_plug = bpy.data.objects.get("Rear_Bumper_Plug")
    if old_plug:
        bpy.data.objects.remove(old_plug, do_unlink=True)
    m_plug = bpy.data.meshes.new("Rear_Bumper_Plug_Mesh")
    o_plug = bpy.data.objects.new("Rear_Bumper_Plug", m_plug)
    bpy.context.collection.objects.link(o_plug)
    
    # Fill disk centered at (0.683, 2.083, 0.612)
    pv, pf = [], []
    c_p = mathutils.Vector((0.683, 2.083, 0.612))
    pv.append(c_p)
    n_pts = 16
    r_plug = 0.058
    for i in range(n_pts):
        ang = 2 * math.pi * i / n_pts
        pv.append(c_p + mathutils.Vector((r_plug * math.cos(ang), 0.015, r_plug * math.sin(ang))))
    for i in range(n_pts):
        pf.append((0, i + 1, (i + 1) % n_pts + 1))
    m_plug.from_pydata(pv, [], pf)
    m_plug.update()
    o_plug.data.materials.append(mat_paint)

    # --------------------------------------------------------
    # ROUND 3: CONTINUOUS PROTECTIVE BUMPER RUB STRIPS
    # --------------------------------------------------------
    print("[Round 3] Modeling continuous protective bumper rub strips...")
    mat_trim = get_or_create_mat("Laguna_Trim_Charcoal")
    tr_bsdf = mat_trim.node_tree.nodes.get("Principled BSDF")
    if tr_bsdf:
        tr_bsdf.inputs['Base Color'].default_value = (0.07, 0.07, 0.075, 1.0)
        tr_bsdf.inputs['Metallic'].default_value = 0.0
        tr_bsdf.inputs['Roughness'].default_value = 0.72

    # Remove old bumper strips if any
    for old_s in ["Rub_Strip_Rear_Bumper", "Rub_Strip_Front_L", "Rub_Strip_Front_R"]:
        ob = bpy.data.objects.get(old_s)
        if ob:
            bpy.data.objects.remove(ob, do_unlink=True)

    # Rear Bumper Wraparound Strip (curving across rear bumper at z ~ 0.58-0.62)
    m_rr_strip = bpy.data.meshes.new("Rub_Strip_Rear_Bumper_Mesh")
    o_rr_strip = bpy.data.objects.new("Rub_Strip_Rear_Bumper", m_rr_strip)
    bpy.context.collection.objects.link(o_rr_strip)
    rv, rf = [], []
    # Curve profile along bumper from left side x = -0.88 to right side x = 0.88
    pts_rear = [
        (-0.87, 1.85, 0.59), (-0.85, 1.98, 0.59), (-0.78, 2.08, 0.60),
        (-0.60, 2.15, 0.60), (-0.30, 2.17, 0.60), (0.00, 2.175, 0.60),
        (0.30, 2.17, 0.60), (0.60, 2.15, 0.60), (0.78, 2.08, 0.60),
        (0.85, 1.98, 0.59), (0.87, 1.85, 0.59)
    ]
    h_strip = 0.024
    for idx, (px, py, pz) in enumerate(pts_rear):
        rv.append(mathutils.Vector((px, py, pz - h_strip)))
        rv.append(mathutils.Vector((px, py, pz + h_strip)))
    for i in range(len(pts_rear) - 1):
        i0 = i * 2
        i1 = i0 + 1
        i2 = i0 + 2
        i3 = i0 + 3
        rf.append((i0, i2, i3, i1))
    m_rr_strip.from_pydata(rv, [], rf)
    m_rr_strip.update()
    o_rr_strip.data.materials.append(mat_trim)

    # Front Bumper Corner Strips (L & R)
    for side_name, side_sgn in [("Rub_Strip_Front_L", -1), ("Rub_Strip_Front_R", 1)]:
        m_fr_s = bpy.data.meshes.new(side_name + "_Mesh")
        o_fr_s = bpy.data.objects.new(side_name, m_fr_s)
        bpy.context.collection.objects.link(o_fr_s)
        fv, ff = [], []
        pts_front = [
            (side_sgn * 0.86, -1.82, 0.48),
            (side_sgn * 0.83, -1.98, 0.48),
            (side_sgn * 0.72, -2.08, 0.48),
            (side_sgn * 0.45, -2.14, 0.48)
        ]
        for px, py, pz in pts_front:
            fv.append(mathutils.Vector((px, py, pz - 0.020)))
            fv.append(mathutils.Vector((px, py, pz + 0.020)))
        for i in range(len(pts_front) - 1):
            i0 = i * 2
            ff.append((i0, i0 + 2, i0 + 3, i0 + 1))
        m_fr_s.from_pydata(fv, [], ff)
        m_fr_s.update()
        o_fr_s.data.materials.append(mat_trim)

    # --------------------------------------------------------
    # ROUND 4: AUTHENTIC 16" 7-SPOKE SILVER RENAULT HUBCAPS
    # --------------------------------------------------------
    print("[Round 4] Modeling authentic 16-inch 7-spoke silver wheel covers & civilian tires...")
    # Hide white racing rims and white spoke meshes
    white_race_spokes = [
        'unnamed.037', 'unnamed.040', 'unnamed.044', 'unnamed.046',
        'unnamed.049', 'unnamed.051', 'unnamed.052', 'unnamed.055',
        'unnamed', 'unnamed.002'
    ]
    for wn in white_race_spokes:
        wo = bpy.data.objects.get(wn)
        if wo:
            wo.hide_render = True
            wo.hide_viewport = True

    # Real civilian tire shader
    mat_tire = get_or_create_mat("Laguna_Tire_Rubber")
    t_bsdf = mat_tire.node_tree.nodes.get("Principled BSDF")
    if t_bsdf:
        t_bsdf.inputs['Base Color'].default_value = (0.045, 0.045, 0.048, 1.0)
        t_bsdf.inputs['Metallic'].default_value = 0.0
        t_bsdf.inputs['Roughness'].default_value = 0.88

    # Authentic lacquered silver alloy paint
    mat_alloy = get_or_create_mat("Laguna_Factory_Alloy")
    al_bsdf = mat_alloy.node_tree.nodes.get("Principled BSDF")
    if al_bsdf:
        al_bsdf.inputs['Base Color'].default_value = (0.76, 0.77, 0.79, 1.0)
        al_bsdf.inputs['Metallic'].default_value = 0.25
        al_bsdf.inputs['Roughness'].default_value = 0.28
        al_bsdf.inputs['Coat Weight'].default_value = 0.40
        al_bsdf.inputs['Coat Roughness'].default_value = 0.12

    # Chrome for center diamond
    mat_chrome = get_or_create_mat("Laguna_Chrome")

    # Dark cavity behind spokes
    mat_cavity = get_or_create_mat("Laguna_Wheel_Cavity")
    c_bsdf = mat_cavity.node_tree.nodes.get("Principled BSDF")
    if c_bsdf:
        c_bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.022, 1.0)
        c_bsdf.inputs['Metallic'].default_value = 0.1
        c_bsdf.inputs['Roughness'].default_value = 0.85

    # Rebuild 4 clean 7-spoke wheels
    wheel_data = [
        ("Wheel_Cap_FR",  0.865, -1.34, 0.32,  1),
        ("Wheel_Cap_FL", -0.865, -1.34, 0.32, -1),
        ("Wheel_Cap_RR",  0.855,  1.32, 0.32,  1),
        ("Wheel_Cap_RL", -0.855,  1.32, 0.32, -1)
    ]

    for name, wx, wy, wz, side in wheel_data:
        old_cap = bpy.data.objects.get(name)
        if old_cap:
            bpy.data.objects.remove(old_cap, do_unlink=True)

        m_cap = bpy.data.meshes.new(name + "_Mesh")
        o_cap = bpy.data.objects.new(name, m_cap)
        bpy.context.collection.objects.link(o_cap)

        wv, wf = [], []
        mat_slots = [] # list of (face_index, mat_idx)

        # Center point
        cp = mathutils.Vector((wx + side * 0.025, wy, wz))

        # 1. Dark backing plate (radius 0.200 m, depth 0.015 m inward)
        back_center_idx = len(wv)
        wv.append(cp - mathutils.Vector((side * 0.018, 0, 0)))
        n_back = 28
        back_ring_start = len(wv)
        for i in range(n_back):
            a = 2 * math.pi * i / n_back
            wv.append(cp - mathutils.Vector((side * 0.018, 0, 0)) + mathutils.Vector((0, 0.200 * math.cos(a), 0.200 * math.sin(a))))
        for i in range(n_back):
            f_idx = len(wf)
            wf.append((back_center_idx, back_ring_start + i, back_ring_start + (i + 1) % n_back))
            mat_slots.append((f_idx, 2)) # cavity mat

        # 2. Outer silver rim lip (continuous ring at r = 0.200 to 0.212)
        outer_rim_start = len(wv)
        n_rim = 28
        for i in range(n_rim):
            a = 2 * math.pi * i / n_rim
            wv.append(cp + mathutils.Vector((0, 0.192 * math.cos(a), 0.192 * math.sin(a))))
            wv.append(cp + mathutils.Vector((0, 0.208 * math.cos(a), 0.208 * math.sin(a))))
        for i in range(n_rim):
            i0 = outer_rim_start + i * 2
            i1 = i0 + 1
            next_i = (i + 1) % n_rim
            i2 = outer_rim_start + next_i * 2 + 1
            i3 = outer_rim_start + next_i * 2
            f_idx = len(wf)
            wf.append((i0, i1, i2, i3))
            mat_slots.append((f_idx, 0)) # alloy mat

        # 3. Inner Hub (radius 0.065 m)
        hub_center_idx = len(wv)
        wv.append(cp + mathutils.Vector((side * 0.004, 0, 0))) # slight hub crown
        hub_ring_start = len(wv)
        n_spokes = 7
        n_hub_pts = n_spokes * 4 # 28 pts around hub
        for i in range(n_hub_pts):
            a = 2 * math.pi * i / n_hub_pts
            wv.append(cp + mathutils.Vector((side * 0.002, 0.065 * math.cos(a), 0.065 * math.sin(a))))
        for i in range(n_hub_pts):
            f_idx = len(wf)
            wf.append((hub_center_idx, hub_ring_start + i, hub_ring_start + (i + 1) % n_hub_pts))
            mat_slots.append((f_idx, 0)) # alloy mat

        # 4. Seven distinct wide spokes bridging inner hub to outer rim
        # For each of the 7 spokes, bridge 2 hub segments to 2 rim segments
        for s in range(n_spokes):
            h_start = hub_ring_start + (s * 4)
            h_next = hub_ring_start + (s * 4 + 2)
            r_start = outer_rim_start + (s * 4) * 2
            r_next = outer_rim_start + (s * 4 + 2) * 2

            # Solid silver spoke quad
            f_idx = len(wf)
            wf.append((h_start, h_next, r_next, r_start))
            mat_slots.append((f_idx, 0)) # alloy mat

        # 5. Polished Chrome Renault Diamond centered on the hubcap
        dia_start = len(wv)
        dx = cp.x + side * 0.008
        dy, dz = cp.y, cp.z
        sy, sz = 0.016, 0.026
        wv.append(mathutils.Vector((dx, dy, dz + sz)))
        wv.append(mathutils.Vector((dx, dy + sy, dz)))
        wv.append(mathutils.Vector((dx, dy, dz - sz)))
        wv.append(mathutils.Vector((dx, dy - sy, dz)))
        f_idx = len(wf)
        wf.append((dia_start, dia_start + 1, dia_start + 2, dia_start + 3))
        mat_slots.append((f_idx, 1)) # chrome mat

        m_cap.from_pydata(wv, [], wf)
        m_cap.update()

        # Add materials: 0=Laguna_Factory_Alloy, 1=Laguna_Chrome, 2=Laguna_Wheel_Cavity
        o_cap.data.materials.append(mat_alloy)
        o_cap.data.materials.append(mat_chrome)
        o_cap.data.materials.append(mat_cavity)

        # Assign per-face material
        for f_idx, mat_id in mat_slots:
            if f_idx < len(m_cap.polygons):
                m_cap.polygons[f_idx].material_index = mat_id

    # --------------------------------------------------------
    # ROUND 5: FLUSH HEADLIGHT LENSES & DUAL PROJECTORS
    # --------------------------------------------------------
    print("[Round 5] Upgrading headlights with flush outer lenses and dual chrome projector bowls...")
    mat_hl_glass = get_or_create_mat("Laguna_Headlight_Glass")
    hlg_bsdf = mat_hl_glass.node_tree.nodes.get("Principled BSDF")
    if hlg_bsdf:
        hlg_bsdf.inputs['Base Color'].default_value = (0.95, 0.97, 1.0, 1.0)
        hlg_bsdf.inputs['Roughness'].default_value = 0.04
        hlg_bsdf.inputs['Transmission Weight'].default_value = 0.88
        hlg_bsdf.inputs['Alpha'].default_value = 0.35
        hlg_bsdf.inputs['IOR'].default_value = 1.51
        hlg_bsdf.inputs['Coat Weight'].default_value = 1.0
        hlg_bsdf.inputs['Coat Roughness'].default_value = 0.02

    mat_reflector = get_or_create_mat("Laguna_Headlight_Reflector")
    ref_bsdf = mat_reflector.node_tree.nodes.get("Principled BSDF")
    if ref_bsdf:
        ref_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.96, 1.0)
        ref_bsdf.inputs['Metallic'].default_value = 0.95
        ref_bsdf.inputs['Roughness'].default_value = 0.06

    mat_amber = get_or_create_mat("Laguna_Amber_Indicator")
    amb_bsdf = mat_amber.node_tree.nodes.get("Principled BSDF")
    if amb_bsdf:
        amb_bsdf.inputs['Base Color'].default_value = (1.0, 0.42, 0.04, 1.0)
        amb_bsdf.inputs['Roughness'].default_value = 0.15
        if 'Emission Color' in amb_bsdf.inputs:
            amb_bsdf.inputs['Emission Color'].default_value = (1.0, 0.40, 0.03, 1.0)
            amb_bsdf.inputs['Emission Strength'].default_value = 0.8

    # Ensure headlight glass meshes are active
    for hg_name in ['unnamed.017', 'unnamed.019', 'unnamed.070', 'unnamed.071']:
        hg = bpy.data.objects.get(hg_name)
        if hg:
            hg.hide_render = False
            hg.hide_viewport = False
            hg.data.materials.clear()
            hg.data.materials.append(mat_hl_glass)

    # Rebuild Projector Assemblies inside the housings
    for side_name, side_x in [("Headlight_Reflector_L", -0.58), ("Headlight_Reflector_R", 0.58)]:
        old_hl = bpy.data.objects.get(side_name)
        if old_hl:
            bpy.data.objects.remove(old_hl, do_unlink=True)
        m_hl = bpy.data.meshes.new(side_name + "_Mesh")
        o_hl = bpy.data.objects.new(side_name, m_hl)
        bpy.context.collection.objects.link(o_hl)

        hv, hf = [], []
        # Outer projector bowl (low beam)
        p1 = mathutils.Vector((side_x, -2.01, 0.56))
        # Inner reflector bowl (high beam)
        p2 = mathutils.Vector((side_x - (0.08 if side_x > 0 else -0.08), -2.00, 0.56))
        # Amber indicator bulb in outer corner
        p3 = mathutils.Vector((side_x + (0.12 if side_x > 0 else -0.12), -1.97, 0.56))

        for pt, rad in [(p1, 0.036), (p2, 0.032)]:
            c_idx = len(hv)
            hv.append(pt - mathutils.Vector((0, 0.020, 0))) # recessed center
            n_pts = 12
            for i in range(n_pts):
                ang = 2 * math.pi * i / n_pts
                hv.append(pt + mathutils.Vector((rad * math.cos(ang), 0.005, rad * math.sin(ang))))
            for i in range(n_pts):
                hf.append((c_idx, c_idx + 1 + i, c_idx + 1 + (i + 1) % n_pts))

        # Amber bulb
        c_amb = len(hv)
        hv.append(p3)
        for i in range(8):
            ang = 2 * math.pi * i / 8
            hv.append(p3 + mathutils.Vector((0.018 * math.cos(ang), 0.005, 0.018 * math.sin(ang))))
        for i in range(8):
            hf.append((c_amb, c_amb + 1 + i, c_amb + 1 + (i + 1) % 8))

        m_hl.from_pydata(hv, [], hf)
        m_hl.update()
        o_hl.data.materials.append(mat_reflector)
        o_hl.data.materials.append(mat_amber)
        # Assign amber material to bulb faces
        for poly_idx in range(len(m_hl.polygons) - 8, len(m_hl.polygons)):
            m_hl.polygons[poly_idx].material_index = 1

    # --------------------------------------------------------
    # ROUND 6: SPLIT GRILLE SLATS, CENTER NOSE BEAK & FOGS
    # --------------------------------------------------------
    print("[Round 6] Styling front nose beak, split grille slats, and fog lights...")
    old_dia = bpy.data.objects.get("Front_Renault_Diamond")
    if old_dia:
        bpy.data.objects.remove(old_dia, do_unlink=True)
    m_dia = bpy.data.meshes.new("Front_Renault_Diamond_Mesh")
    o_dia = bpy.data.objects.new("Front_Renault_Diamond", m_dia)
    bpy.context.collection.objects.link(o_dia)
    dv, df = [], []
    c_dia = mathutils.Vector((0.0, -2.145, 0.625))
    sy, sz = 0.026, 0.042
    # Outer diamond facets
    dv.append(c_dia + mathutils.Vector((0, -0.012, sz)))
    dv.append(c_dia + mathutils.Vector((sy, -0.010, 0)))
    dv.append(c_dia + mathutils.Vector((0, -0.012, -sz)))
    dv.append(c_dia + mathutils.Vector((-sy, -0.010, 0)))
    dv.append(c_dia + mathutils.Vector((0, -0.018, 0))) # central peak
    df.append((0, 1, 4))
    df.append((1, 2, 4))
    df.append((2, 3, 4))
    df.append((3, 0, 4))
    m_dia.from_pydata(dv, [], df)
    m_dia.update()
    o_dia.data.materials.append(mat_chrome)

    # Front Split Grille Horizontal Slats (Left & Right of beak)
    for gr_name, gr_x in [("Grille_Slats_L", -0.22), ("Grille_Slats_R", 0.22)]:
        old_gr = bpy.data.objects.get(gr_name)
        if old_gr:
            bpy.data.objects.remove(old_gr, do_unlink=True)
        m_gr = bpy.data.meshes.new(gr_name + "_Mesh")
        o_gr = bpy.data.objects.new(gr_name, m_gr)
        bpy.context.collection.objects.link(o_gr)
        gv, gf = [], []
        # 3 horizontal slats
        for slat_i in range(3):
            z_slat = 0.60 + slat_i * 0.018
            w_slat = 0.14
            gv.append(mathutils.Vector((gr_x - w_slat, -2.11, z_slat - 0.004)))
            gv.append(mathutils.Vector((gr_x + w_slat, -2.11, z_slat - 0.004)))
            gv.append(mathutils.Vector((gr_x + w_slat, -2.11, z_slat + 0.004)))
            gv.append(mathutils.Vector((gr_x - w_slat, -2.11, z_slat + 0.004)))
            base_v = slat_i * 4
            gf.append((base_v, base_v + 1, base_v + 2, base_v + 3))
        m_gr.from_pydata(gv, [], gf)
        m_gr.update()
        o_gr.data.materials.append(mat_trim)

    # Circular fog lights in lower bumper pods
    for fog_name, fog_x in [("Fog_Light_L", -0.62), ("Fog_Light_R", 0.62)]:
        old_fog = bpy.data.objects.get(fog_name)
        if old_fog:
            bpy.data.objects.remove(old_fog, do_unlink=True)
        m_fog = bpy.data.meshes.new(fog_name + "_Mesh")
        o_fog = bpy.data.objects.new(fog_name, m_fog)
        bpy.context.collection.objects.link(o_fog)
        fog_v, fog_f = [], []
        cp_fog = mathutils.Vector((fog_x, -2.09, 0.36))
        fog_v.append(cp_fog)
        n_p = 12
        r_f = 0.038
        for i in range(n_p):
            a = 2 * math.pi * i / n_p
            fog_v.append(cp_fog + mathutils.Vector((r_f * math.cos(a), 0.008, r_f * math.sin(a))))
        for i in range(n_p):
            fog_f.append((0, i + 1, (i + 1) % n_p + 1))
        m_fog.from_pydata(fog_v, [], fog_f)
        m_fog.update()
        o_fog.data.materials.append(mat_reflector)

    # --------------------------------------------------------
    # ROUND 7: PROPER WIPER POSITIONING IN COWL & REAR GLASS
    # --------------------------------------------------------
    print("[Round 7] Positioning front wipers into cowl tray and aligning rear wiper...")
    mat_black = get_or_create_mat("Laguna_Pillar_Black")

    for w_name in ["Front_Wiper_Driver", "Front_Wiper_Pass", "Rear_Wiper"]:
        ow = bpy.data.objects.get(w_name)
        if ow:
            bpy.data.objects.remove(ow, do_unlink=True)

    # Driver wiper (parked in black cowl at base of windshield y ~ -1.14, z ~ 0.77)
    m_wd = bpy.data.meshes.new("Front_Wiper_Driver_Mesh")
    o_wd = bpy.data.objects.new("Front_Wiper_Driver", m_wd)
    bpy.context.collection.objects.link(o_wd)
    # Pivot at (-0.46, -1.16, 0.77), blade extending across to (-0.02, -1.14, 0.78)
    wd_v = [
        mathutils.Vector((-0.46, -1.16, 0.765)),
        mathutils.Vector((-0.02, -1.14, 0.778)),
        mathutils.Vector((-0.02, -1.14, 0.786)),
        mathutils.Vector((-0.46, -1.16, 0.773))
    ]
    m_wd.from_pydata(wd_v, [], [(0, 1, 2, 3)])
    m_wd.update()
    o_wd.data.materials.append(mat_black)

    # Passenger wiper (parked along passenger side cowl)
    m_wp = bpy.data.meshes.new("Front_Wiper_Pass_Mesh")
    o_wp = bpy.data.objects.new("Front_Wiper_Pass", m_wp)
    bpy.context.collection.objects.link(o_wp)
    wp_v = [
        mathutils.Vector((0.08, -1.14, 0.778)),
        mathutils.Vector((0.52, -1.15, 0.772)),
        mathutils.Vector((0.52, -1.15, 0.780)),
        mathutils.Vector((0.08, -1.14, 0.786))
    ]
    m_wp.from_pydata(wp_v, [], [(0, 1, 2, 3)])
    m_wp.update()
    o_wp.data.materials.append(mat_black)

    # Rear liftback wiper: flush on rear window glass (y ~ 1.50 to 1.78, z ~ 1.01 to 1.15)
    m_rw = bpy.data.meshes.new("Rear_Wiper_Mesh")
    o_rw = bpy.data.objects.new("Rear_Wiper", m_rw)
    bpy.context.collection.objects.link(o_rw)
    # Pivot near rear wiper motor at (0.24, 1.75, 1.01), arm extending diagonally across glass
    rw_v = [
        mathutils.Vector((0.26, 1.76, 1.008)),
        mathutils.Vector((-0.18, 1.48, 1.142)),
        mathutils.Vector((-0.18, 1.48, 1.152)),
        mathutils.Vector((0.26, 1.76, 1.018))
    ]
    m_rw.from_pydata(rw_v, [], [(0, 1, 2, 3)])
    m_rw.update()
    o_rw.data.materials.append(mat_black)

    # --------------------------------------------------------
    # ROUND 8: TAILLIGHT CLUSTERS & HIGH-MOUNT 3RD BRAKE LIGHT
    # --------------------------------------------------------
    print("[Round 8] Refining two-tone taillights and 3rd brake light...")
    mat_ruby = get_or_create_mat("Laguna_Taillight_Ruby")
    rb_bsdf = mat_ruby.node_tree.nodes.get("Principled BSDF")
    if rb_bsdf:
        rb_bsdf.inputs['Base Color'].default_value = (0.75, 0.03, 0.03, 1.0)
        rb_bsdf.inputs['Roughness'].default_value = 0.06
        rb_bsdf.inputs['Transmission Weight'].default_value = 0.65
        rb_bsdf.inputs['Alpha'].default_value = 0.85
        rb_bsdf.inputs['Coat Weight'].default_value = 1.0
        rb_bsdf.inputs['Coat Roughness'].default_value = 0.02
        if 'Emission Color' in rb_bsdf.inputs:
            rb_bsdf.inputs['Emission Color'].default_value = (0.80, 0.02, 0.02, 1.0)
            rb_bsdf.inputs['Emission Strength'].default_value = 0.4

    mat_tl_clear = get_or_create_mat("Laguna_Taillight_Clear")
    tlc_bsdf = mat_tl_clear.node_tree.nodes.get("Principled BSDF")
    if tlc_bsdf:
        tlc_bsdf.inputs['Base Color'].default_value = (0.92, 0.93, 0.95, 1.0)
        tlc_bsdf.inputs['Roughness'].default_value = 0.08
        tlc_bsdf.inputs['Transmission Weight'].default_value = 0.82
        tlc_bsdf.inputs['Alpha'].default_value = 0.60

    # Ensure taillight meshes are properly assigned
    for r_tl in ['unnamed.010', 'unnamed.015', 'unnamed.016', 'unnamed.032', 'unnamed.033']:
        o = bpy.data.objects.get(r_tl)
        if o:
            o.hide_render = False
            o.hide_viewport = False
            o.data.materials.clear()
            o.data.materials.append(mat_ruby)

    for c_tl in ['unnamed.018', 'unnamed.020']:
        o = bpy.data.objects.get(c_tl)
        if o:
            o.hide_render = False
            o.hide_viewport = False
            o.data.materials.clear()
            o.data.materials.append(mat_tl_clear)

    # Slim 3rd brake light on decklid lip
    old_3rd = bpy.data.objects.get("Third_Brake_Light")
    if old_3rd:
        bpy.data.objects.remove(old_3rd, do_unlink=True)
    m_3rd = bpy.data.meshes.new("Third_Brake_Light_Mesh")
    o_3rd = bpy.data.objects.new("Third_Brake_Light", m_3rd)
    bpy.context.collection.objects.link(o_3rd)
    b3_v = [
        mathutils.Vector((-0.18, 1.88, 0.965)),
        mathutils.Vector(( 0.18, 1.88, 0.965)),
        mathutils.Vector(( 0.18, 1.88, 0.978)),
        mathutils.Vector((-0.18, 1.88, 0.978))
    ]
    m_3rd.from_pydata(b3_v, [], [(0, 1, 2, 3)])
    m_3rd.update()
    o_3rd.data.materials.append(mat_ruby)

    # --------------------------------------------------------
    # ROUND 9: GREEN SOLARGLASS TINT & CIVILIAN COCKPIT
    # --------------------------------------------------------
    print("[Round 9] Calibrating Renault Solarglass tint and dark interior depth...")
    mat_solar = get_or_create_mat("Laguna_Factory_Solarglass")
    sg_bsdf = mat_solar.node_tree.nodes.get("Principled BSDF")
    if sg_bsdf:
        # Subtle green Solarglass hue
        sg_bsdf.inputs['Base Color'].default_value = (0.86, 0.94, 0.90, 1.0)
        sg_bsdf.inputs['Roughness'].default_value = 0.015
        sg_bsdf.inputs['Transmission Weight'].default_value = 0.85
        sg_bsdf.inputs['Alpha'].default_value = 0.32
        sg_bsdf.inputs['IOR'].default_value = 1.52
        sg_bsdf.inputs['Coat Weight'].default_value = 1.0
        sg_bsdf.inputs['Coat Roughness'].default_value = 0.01

    # Apply Solarglass to glass objects
    for g_name in ['unnamed.021', 'unnamed.027']:
        og = bpy.data.objects.get(g_name)
        if og:
            og.hide_render = False
            og.hide_viewport = False
            og.data.materials.clear()
            og.data.materials.append(mat_solar)

    # Dark charcoal interior seating & dashboard
    mat_interior = get_or_create_mat("Laguna_Interior_Charcoal")
    int_bsdf = mat_interior.node_tree.nodes.get("Principled BSDF")
    if int_bsdf:
        int_bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.045, 1.0)
        int_bsdf.inputs['Roughness'].default_value = 0.92

    headrests = [
        ("Headrest_Driver",   -0.34, -0.22, 1.04),
        ("Headrest_Pass",      0.34, -0.22, 1.04),
        ("Headrest_Rear_L",   -0.34,  0.72, 1.02),
        ("Headrest_Rear_R",    0.34,  0.72, 1.02)
    ]
    for hr_name, hx, hy, hz in headrests:
        old_hr = bpy.data.objects.get(hr_name)
        if old_hr:
            bpy.data.objects.remove(old_hr, do_unlink=True)
        m_hr = bpy.data.meshes.new(hr_name + "_Mesh")
        o_hr = bpy.data.objects.new(hr_name, m_hr)
        bpy.context.collection.objects.link(o_hr)
        hw, hh, ht = 0.08, 0.045, 0.03
        hr_v = [
            mathutils.Vector((hx - hw, hy - ht, hz - hh)),
            mathutils.Vector((hx + hw, hy - ht, hz - hh)),
            mathutils.Vector((hx + hw, hy + ht, hz - hh)),
            mathutils.Vector((hx - hw, hy + ht, hz - hh)),
            mathutils.Vector((hx - hw, hy - ht, hz + hh)),
            mathutils.Vector((hx + hw, hy - ht, hz + hh)),
            mathutils.Vector((hx + hw, hy + ht, hz + hh)),
            mathutils.Vector((hx - hw, hy + ht, hz + hh))
        ]
        hr_f = [
            (0, 1, 2, 3), (4, 5, 6, 7), (0, 4, 7, 3),
            (1, 5, 6, 2), (0, 1, 5, 4), (3, 2, 6, 7)
        ]
        m_hr.from_pydata(hr_v, [], hr_f)
        m_hr.update()
        o_hr.data.materials.append(mat_interior)

    # --------------------------------------------------------
    # ROUND 10: TAILGATE BADGING, EURO PLATE, STUDIO STAGING & RENDERS
    # --------------------------------------------------------
    print("[Round 10] Tailgate badging, European license plate, calibrated lighting & 1080p renders...")
    # Tailgate Renault Diamond
    old_rd = bpy.data.objects.get("Rear_Renault_Diamond")
    if old_rd:
        bpy.data.objects.remove(old_rd, do_unlink=True)
    m_rd = bpy.data.meshes.new("Rear_Renault_Diamond_Mesh")
    o_rd = bpy.data.objects.new("Rear_Renault_Diamond", m_rd)
    bpy.context.collection.objects.link(o_rd)
    c_rd = mathutils.Vector((0.0, 2.185, 0.880))
    ry, rz = 0.022, 0.036
    rd_v = [
        c_rd + mathutils.Vector((0, 0.008, rz)),
        c_rd + mathutils.Vector((ry, 0.006, 0)),
        c_rd + mathutils.Vector((0, 0.008, -rz)),
        c_rd + mathutils.Vector((-ry, 0.006, 0)),
        c_rd + mathutils.Vector((0, 0.014, 0))
    ]
    rd_f = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
    m_rd.from_pydata(rd_v, [], rd_f)
    m_rd.update()
    o_rd.data.materials.append(mat_chrome)

    # European License Plate (recessed into tailgate)
    old_lp = bpy.data.objects.get("License_Plate")
    if old_lp:
        bpy.data.objects.remove(old_lp, do_unlink=True)
    m_lp = bpy.data.meshes.new("License_Plate_Mesh")
    o_lp = bpy.data.objects.new("License_Plate", m_lp)
    bpy.context.collection.objects.link(o_lp)
    mat_plate = get_or_create_mat("Laguna_License_Plate")
    lp_bsdf = mat_plate.node_tree.nodes.get("Principled BSDF")
    if lp_bsdf:
        lp_bsdf.inputs['Base Color'].default_value = (0.90, 0.91, 0.93, 1.0)
        lp_bsdf.inputs['Roughness'].default_value = 0.25
        lp_bsdf.inputs['Coat Weight'].default_value = 0.60
    # 520mm x 110mm European plate
    pw, ph = 0.26, 0.055
    lp_v = [
        mathutils.Vector((-pw, 2.185, 0.745 - ph)),
        mathutils.Vector(( pw, 2.185, 0.745 - ph)),
        mathutils.Vector(( pw, 2.185, 0.745 + ph)),
        mathutils.Vector((-pw, 2.185, 0.745 + ph))
    ]
    m_lp.from_pydata(lp_v, [], [(0, 1, 2, 3)])
    m_lp.update()
    o_lp.data.materials.append(mat_plate)

    # Lighting: Balanced daylight environment (Nishita sky)
    world = scene.world
    nt = world.node_tree
    node_bg = nt.nodes.get("ShaderNodeBackground") or nt.nodes.get("Background")
    node_sky = nt.nodes.get("ShaderNodeTexSky")
    if node_sky:
        node_sky.sky_type = 'MULTIPLE_SCATTERING'
        node_sky.sun_elevation = math.radians(42.0)
        node_sky.sun_rotation = math.radians(-38.0)
        node_sky.altitude = 25.0
        node_sky.air_density = 1.0
        if hasattr(node_sky, 'aerosol_density'):
            node_sky.aerosol_density = 0.30
        node_sky.ozone_density = 1.5
        node_sky.sun_disc = True
        node_sky.ground_albedo = 0.15

    if node_bg:
        # Reduced background strength to preserve deep color tones
        node_bg.inputs['Strength'].default_value = 0.65

    # AgX Color Management with balanced exposure
    scene.view_settings.view_transform = 'AgX'
    try:
        scene.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    # Exposure adjusted so paint does not blow out to pure white
    scene.view_settings.exposure = -2.50

    # Save updated blend file
    blend_path = os.path.abspath(r"blender\laguna_master.blend")
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"[Round 10] Saved updated master blend file: {blend_path}")

    # Camera rendering
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    cam = scene.camera
    if not cam:
        cam_data = bpy.data.cameras.new("Studio_Cam")
        cam = bpy.data.objects.new("Studio_Cam", cam_data)
        bpy.context.collection.objects.link(cam)
        scene.camera = cam

    out_front = os.path.abspath(r"laguna_front.png")
    out_rear = os.path.abspath(r"laguna_rear.png")
    out_pres = os.path.abspath(r"laguna_presentation.png")

    # Front 3/4 Render: Cam at (-4.10, -4.35, 1.25)
    print("[Round 10] Rendering Front 3/4 validation angle...")
    cam.location = mathutils.Vector((-4.10, -4.35, 1.25))
    target_front = mathutils.Vector((0.0, -0.60, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear 3/4 Render: Cam at (3.80, 4.30, 1.35)
    print("[Round 10] Rendering Rear 3/4 validation angle...")
    cam.location = mathutils.Vector((3.80, 4.30, 1.35))
    target_rear = mathutils.Vector((0.0, 0.40, 0.65))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    # Copy presentation images
    shutil.copy2(out_front, out_pres)
    shutil.copy2(out_front, os.path.join(ARTIFACT_DIR, "laguna_front.png"))
    shutil.copy2(out_rear, os.path.join(ARTIFACT_DIR, "laguna_rear.png"))
    shutil.copy2(out_pres, os.path.join(ARTIFACT_DIR, "laguna_presentation.png"))

    print("==========================================================")
    print("10-ROUND REFINEMENT PASS SUCCESSFULLY COMPLETED!")
    print("==========================================================")

if __name__ == "__main__":
    execute_10_rounds()
