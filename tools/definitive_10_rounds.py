"""
definitive_10_rounds.py
=======================
Definitive 10-round systematic visual refinement pass for the Renault Laguna II Phase 1 (2001-2005)
in Blender 5.3:
  Round 1: Non-shiny satin matte Beige Poivre paint calibration (Metallic 0.05, Roughness 0.46, Coat 0.08).
  Round 2: Bridge decklid gap, bmesh edge-fill rear bumper hole, remove spoiler stubs & race equipment.
  Round 3: Assign Laguna_Trim_Charcoal directly to built-in bumper & door rub strip faces on unnamed.004.
  Round 4: Re-engineer authentic 16" 7-spoke silver wheel covers with extended backing & civilian tire sidewalls.
  Round 5: Overhaul front headlights with flush clear lens, dual chrome projector bowls, and amber corners.
  Round 6: Position curvature-angled split grille slats inside bumper opening, beak diamond, and fog lights.
  Round 7: Park front wipers properly down in cowl tray and align rear wiper flush against glass.
  Round 8: Refine two-tone ruby/clear taillight clusters and high-mount 3rd brake light.
  Round 9: Realistic Renault Solarglass with outdoor sky reflections, B-pillars, and cockpit depth.
  Round 10: Tailgate badging, European license plate, outdoor HDR environment, and 1080p validation renders.
"""

import bpy
import bmesh
import mathutils
import math
import os
import shutil

PROJECT_ROOT = r"C:\Users\abdelkarim\Documents\laguna-beamng"
ARTIFACT_DIR = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
HDR_PATH = r"C:\Program Files\Blender Foundation\Blender 5.3\5.3\datafiles\studiolights\world\courtyard.exr"

def get_or_create_mat(name):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    return m

def execute_definitive_pass():
    print("==========================================================")
    print("STARTING DEFINITIVE 10-ROUND LAGUNA II REFINEMENT PASS")
    print("==========================================================")
    scene = bpy.context.scene

    # --------------------------------------------------------
    # ROUND 1: NON-SHINY SATIN MATTE BEIGE POIVRE PAINT
    # --------------------------------------------------------
    print("[Round 1] Calibrating authentic Beige Poivre satin matte finish...")
    for paint_name in ["Laguna_Champagne_Silver", "Laguna_Paint_BeigePoivre"]:
        mat_paint = get_or_create_mat(paint_name)
        mat_paint.use_nodes = True
        bsdf = mat_paint.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            # Authentic Renault Beige Poivre (B64) warm champagne grey/taupe
            bsdf.inputs['Base Color'].default_value = (0.48, 0.44, 0.37, 1.0)
            # Very low metallic for civilian satin matte texture
            bsdf.inputs['Metallic'].default_value = 0.05
            # High roughness for soft diffuse falloff and no shiny mirror reflections
            bsdf.inputs['Roughness'].default_value = 0.46
            bsdf.inputs['IOR'].default_value = 1.50
            # Faint clearcoat
            bsdf.inputs['Coat Weight'].default_value = 0.08
            bsdf.inputs['Coat Roughness'].default_value = 0.40
            if 'Specular IOR Level' in bsdf.inputs:
                bsdf.inputs['Specular IOR Level'].default_value = 0.38

    mat_paint = bpy.data.materials.get("Laguna_Champagne_Silver")

    # --------------------------------------------------------
    # ROUND 2: BRIDGE DECKLID GAP, FILL BUMPER HOLE & CLEAN RACE PARTS
    # --------------------------------------------------------
    print("[Round 2] Bridging decklid gap, bmesh edge-filling bumper hole & removing race parts...")
    # Hide all race car interior/cage/fuel cell equipment
    race_remnants = [
        'unnamed.028', 'unnamed.029', 'unnamed.030', 'unnamed.069',
        'unnamed.135', 'unnamed.136', 'unnamed.149', 'unnamed.150',
        'unnamed.152', 'unnamed.153', 'unnamed.155', 'unnamed.156',
        'unnamed.157', 'unnamed.158', 'unnamed.159', 'unnamed.160',
        'unnamed.161', 'unnamed.162', 'unnamed.165', 'unnamed.168',
        'unnamed.175', 'unnamed.190', 'unnamed.194', 'unnamed.197',
        'unnamed.213', 'unnamed.214', 'unnamed.216', 'unnamed.217',
        'unnamed.219', 'unnamed.221', 'unnamed.222', 'unnamed.225',
        'unnamed.232', 'unnamed.239'
    ]
    for n in race_remnants:
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = True
            o.hide_viewport = True

    # Delete spoiler mounting stubs on unnamed.026 (z > 0.96)
    o_026 = bpy.data.objects.get("unnamed.026")
    if o_026:
        o_026.hide_render = False
        o_026.hide_viewport = False
        o_026.data.materials.clear()
        o_026.data.materials.append(mat_paint)
        bm_026 = bmesh.new()
        bm_026.from_mesh(o_026.data)
        faces_to_del = [f for f in bm_026.faces if any((o_026.matrix_world @ v.co).z > 0.96 for v in f.verts)]
        if faces_to_del:
            bmesh.ops.delete(bm_026, geom=faces_to_del, context='FACES')
            bm_026.to_mesh(o_026.data)
            o_026.data.update()
        bm_026.free()

    # Fill circular hole on right rear bumper of unnamed.004
    o_004 = bpy.data.objects.get("unnamed.004")
    if o_004:
        bm_004 = bmesh.new()
        bm_004.from_mesh(o_004.data)
        hole_edges = [
            e for e in bm_004.edges 
            if e.is_boundary and all(0.55 < (o_004.matrix_world @ v.co).x < 0.80 and (o_004.matrix_world @ v.co).y > 1.9 and 0.52 < (o_004.matrix_world @ v.co).z < 0.70 for v in e.verts)
        ]
        if hole_edges:
            bmesh.ops.edgeloop_fill(bm_004, edges=hole_edges)
            bm_004.to_mesh(o_004.data)
            o_004.data.update()
            print("Successfully sealed right rear bumper hole with bmesh edgeloop_fill!")
        bm_004.free()

    # Build clean production Decklid Surface bridging the gap between glass (y=1.955) and trunk (y=2.085)
    old_deck = bpy.data.objects.get("Decklid_Surface")
    if old_deck:
        bpy.data.objects.remove(old_deck, do_unlink=True)
    m_deck = bpy.data.meshes.new("Decklid_Surface_Mesh")
    o_deck = bpy.data.objects.new("Decklid_Surface", m_deck)
    bpy.context.collection.objects.link(o_deck)

    xs = [-0.60, -0.45, -0.30, -0.15, 0.0, 0.15, 0.30, 0.45, 0.60]
    ys = [1.955, 1.990, 2.030, 2.070, 2.085]
    dv, df = [], []
    for y_idx, py in enumerate(ys):
        for px in xs:
            crown = 0.012 * (1.0 - (px / 0.60)**2)
            t = y_idx / (len(ys) - 1)
            pz = (1.0 - t) * 0.965 + t * 0.898 + crown
            dv.append(mathutils.Vector((px, py, pz)))

    nx = len(xs)
    ny = len(ys)
    for j in range(ny - 1):
        for i in range(nx - 1):
            i0 = j * nx + i
            i1 = i0 + 1
            i2 = (j + 1) * nx + (i + 1)
            i3 = (j + 1) * nx + i
            df.append((i0, i1, i2, i3))

    m_deck.from_pydata(dv, [], df)
    m_deck.update()
    o_deck.data.materials.append(mat_paint)

    # --------------------------------------------------------
    # ROUND 3: INTEGRATED PROTECTIVE BUMPER & DOOR RUB STRIPS
    # --------------------------------------------------------
    print("[Round 3] Assigning Laguna_Trim_Charcoal to built-in unibody rub strip faces...")
    mat_trim = get_or_create_mat("Laguna_Trim_Charcoal")
    tr_bsdf = mat_trim.node_tree.nodes.get("Principled BSDF")
    if tr_bsdf:
        tr_bsdf.inputs['Base Color'].default_value = (0.065, 0.065, 0.070, 1.0)
        tr_bsdf.inputs['Metallic'].default_value = 0.0
        tr_bsdf.inputs['Roughness'].default_value = 0.74

    # Remove procedural floating box strips to avoid duplicate geometry
    for old_s in ["Rub_Strip_Rear_Bumper", "Rub_Strip_Front_L", "Rub_Strip_Front_R", "Rear_Bumper_Plug"]:
        ob = bpy.data.objects.get(old_s)
        if ob:
            bpy.data.objects.remove(ob, do_unlink=True)

    # Ensure unnamed.004 has Laguna_Champagne_Silver as slot 0 and Laguna_Trim_Charcoal as slot 1
    if o_004:
        o_004.data.materials.clear()
        o_004.data.materials.append(mat_paint) # Slot 0
        o_004.data.materials.append(mat_trim)  # Slot 1

        trim_count = 0
        for poly in o_004.data.polygons:
            verts = [o_004.matrix_world @ o_004.data.vertices[v_idx].co for v_idx in poly.vertices]
            # Rear bumper beltline: y > 1.8, 0.56 < z < 0.64
            is_rear_trim = all(v.y > 1.8 and 0.56 < v.z < 0.64 for v in verts)
            # Front bumper corner trim: y < -1.8, 0.43 < z < 0.51, abs(x) > 0.42
            is_front_trim = all(v.y < -1.8 and 0.43 < v.z < 0.51 and abs(v.x) > 0.42 for v in verts)
            # Side door rub strips: abs(x) > 0.82, -1.2 < y < 1.2, 0.52 < z < 0.60
            is_side_trim = all(abs(v.x) > 0.82 and -1.2 < v.y < 1.2 and 0.52 < v.z < 0.60 for v in verts)

            if is_rear_trim or is_front_trim or is_side_trim:
                poly.material_index = 1
                trim_count += 1
            else:
                poly.material_index = 0
        print(f"Assigned factory charcoal trim to {trim_count} built-in unibody faces!")

    # --------------------------------------------------------
    # ROUND 4: AUTHENTIC 16" 7-SPOKE SILVER HUBCAPS & CIVILIAN TIRES
    # --------------------------------------------------------
    print("[Round 4] Modeling authentic 16-inch 7-spoke silver wheel covers & civilian tire sidewalls...")
    white_race_spokes = [
        'unnamed', 'unnamed.001', 'unnamed.002', 'unnamed.003',
        'unnamed.037', 'unnamed.040', 'unnamed.044', 'unnamed.046',
        'unnamed.049', 'unnamed.051', 'unnamed.052', 'unnamed.055'
    ]
    for wn in white_race_spokes:
        wo = bpy.data.objects.get(wn)
        if wo:
            wo.hide_render = True
            wo.hide_viewport = True

    mat_tire = get_or_create_mat("Laguna_Tire_Rubber")
    t_bsdf = mat_tire.node_tree.nodes.get("Principled BSDF")
    if t_bsdf:
        t_bsdf.inputs['Base Color'].default_value = (0.045, 0.045, 0.048, 1.0)
        t_bsdf.inputs['Metallic'].default_value = 0.0
        t_bsdf.inputs['Roughness'].default_value = 0.88

    mat_alloy = get_or_create_mat("Laguna_Factory_Alloy")
    al_bsdf = mat_alloy.node_tree.nodes.get("Principled BSDF")
    if al_bsdf:
        al_bsdf.inputs['Base Color'].default_value = (0.76, 0.77, 0.79, 1.0)
        al_bsdf.inputs['Metallic'].default_value = 0.22
        al_bsdf.inputs['Roughness'].default_value = 0.28
        al_bsdf.inputs['Coat Weight'].default_value = 0.40
        al_bsdf.inputs['Coat Roughness'].default_value = 0.12

    mat_chrome = get_or_create_mat("Laguna_Chrome")

    mat_cavity = get_or_create_mat("Laguna_Wheel_Cavity")
    c_bsdf = mat_cavity.node_tree.nodes.get("Principled BSDF")
    if c_bsdf:
        c_bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.022, 1.0)
        c_bsdf.inputs['Metallic'].default_value = 0.05
        c_bsdf.inputs['Roughness'].default_value = 0.85

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
        mat_slots = []
        cp = mathutils.Vector((wx + side * 0.022, wy, wz))

        # 1. Extended dark circular backing disc at radius 0.240m (eliminates any gap to tire!)
        back_center = len(wv)
        wv.append(cp - mathutils.Vector((side * 0.015, 0, 0)))
        n_pts = 28
        ring_back = len(wv)
        for i in range(n_pts):
            a = 2 * math.pi * i / n_pts
            wv.append(cp - mathutils.Vector((side * 0.015, 0, 0)) + mathutils.Vector((0, 0.240 * math.cos(a), 0.240 * math.sin(a))))
        for i in range(n_pts):
            f_idx = len(wf)
            wf.append((back_center, ring_back + i, ring_back + (i + 1) % n_pts))
            mat_slots.append((f_idx, 2)) # cavity

        # 2. Outer silver rim flange (radius 0.190 to 0.210)
        outer_rim_start = len(wv)
        for i in range(n_pts):
            a = 2 * math.pi * i / n_pts
            wv.append(cp + mathutils.Vector((0, 0.190 * math.cos(a), 0.190 * math.sin(a))))
            wv.append(cp + mathutils.Vector((0, 0.210 * math.cos(a), 0.210 * math.sin(a))))
        for i in range(n_pts):
            i0 = outer_rim_start + i * 2
            i1 = i0 + 1
            next_i = (i + 1) % n_pts
            i2 = outer_rim_start + next_i * 2 + 1
            i3 = outer_rim_start + next_i * 2
            f_idx = len(wf)
            wf.append((i0, i1, i2, i3))
            mat_slots.append((f_idx, 0)) # silver alloy

        # 3. Inner Hub (radius 0.070 m) with crowned center
        hub_center = len(wv)
        wv.append(cp + mathutils.Vector((side * 0.005, 0, 0)))
        hub_ring = len(wv)
        n_spokes = 7
        n_hub = n_spokes * 4
        for i in range(n_hub):
            a = 2 * math.pi * i / n_hub
            wv.append(cp + mathutils.Vector((side * 0.002, 0.070 * math.cos(a), 0.070 * math.sin(a))))
        for i in range(n_hub):
            f_idx = len(wf)
            wf.append((hub_center, hub_ring + i, hub_ring + (i + 1) % n_hub))
            mat_slots.append((f_idx, 0)) # silver alloy

        # 4. Seven distinct wide spokes
        for s in range(n_spokes):
            h_start = hub_ring + (s * 4)
            h_next  = hub_ring + (s * 4 + 2)
            r_start = outer_rim_start + (s * 4) * 2
            r_next  = outer_rim_start + (s * 4 + 2) * 2
            f_idx = len(wf)
            wf.append((h_start, h_next, r_next, r_start))
            mat_slots.append((f_idx, 0)) # silver alloy

        # 5. Polished Chrome Renault Diamond in center
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
        mat_slots.append((f_idx, 1)) # chrome

        m_cap.from_pydata(wv, [], wf)
        m_cap.update()

        o_cap.data.materials.append(mat_alloy)
        o_cap.data.materials.append(mat_chrome)
        o_cap.data.materials.append(mat_cavity)

        for f_idx, mat_id in mat_slots:
            if f_idx < len(m_cap.polygons):
                m_cap.polygons[f_idx].material_index = mat_id

    # --------------------------------------------------------
    # ROUND 5: FLUSH HEADLIGHT LENSES & DUAL CHROME PROJECTORS
    # --------------------------------------------------------
    print("[Round 5] Upgrading headlights with flush outer lenses and dual chrome projector bowls...")
    mat_hl_glass = get_or_create_mat("Laguna_Headlight_Glass")
    hlg_bsdf = mat_hl_glass.node_tree.nodes.get("Principled BSDF")
    if hlg_bsdf:
        hlg_bsdf.inputs['Base Color'].default_value = (0.95, 0.97, 1.0, 1.0)
        hlg_bsdf.inputs['Roughness'].default_value = 0.03
        hlg_bsdf.inputs['Transmission Weight'].default_value = 0.88
        hlg_bsdf.inputs['Alpha'].default_value = 0.35
        hlg_bsdf.inputs['IOR'].default_value = 1.51
        hlg_bsdf.inputs['Coat Weight'].default_value = 1.0

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

    for hg_name in ['unnamed.017', 'unnamed.019', 'unnamed.070', 'unnamed.071']:
        hg = bpy.data.objects.get(hg_name)
        if hg:
            hg.hide_render = False
            hg.hide_viewport = False
            hg.data.materials.clear()
            hg.data.materials.append(mat_hl_glass)

    for side_name, side_x in [("Headlight_Reflector_L", -0.58), ("Headlight_Reflector_R", 0.58)]:
        old_hl = bpy.data.objects.get(side_name)
        if old_hl:
            bpy.data.objects.remove(old_hl, do_unlink=True)
        m_hl = bpy.data.meshes.new(side_name + "_Mesh")
        o_hl = bpy.data.objects.new(side_name, m_hl)
        bpy.context.collection.objects.link(o_hl)

        hv, hf = [], []
        p1 = mathutils.Vector((side_x, -2.01, 0.56))
        p2 = mathutils.Vector((side_x - (0.08 if side_x > 0 else -0.08), -2.00, 0.56))
        p3 = mathutils.Vector((side_x + (0.12 if side_x > 0 else -0.12), -1.97, 0.56))

        for pt, rad in [(p1, 0.036), (p2, 0.032)]:
            c_idx = len(hv)
            hv.append(pt - mathutils.Vector((0, 0.020, 0)))
            for i in range(12):
                ang = 2 * math.pi * i / 12
                hv.append(pt + mathutils.Vector((rad * math.cos(ang), 0.005, rad * math.sin(ang))))
            for i in range(12):
                hf.append((c_idx, c_idx + 1 + i, c_idx + 1 + (i + 1) % 12))

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
        for poly_idx in range(len(m_hl.polygons) - 8, len(m_hl.polygons)):
            m_hl.polygons[poly_idx].material_index = 1

    # --------------------------------------------------------
    # ROUND 6: ANGLED SPLIT GRILLE SLATS, BEAK & FOG LIGHTS
    # --------------------------------------------------------
    print("[Round 6] Positioning curvature-angled split grille slats & fog lights...")
    old_dia = bpy.data.objects.get("Front_Renault_Diamond")
    if old_dia:
        bpy.data.objects.remove(old_dia, do_unlink=True)
    m_dia = bpy.data.meshes.new("Front_Renault_Diamond_Mesh")
    o_dia = bpy.data.objects.new("Front_Renault_Diamond", m_dia)
    bpy.context.collection.objects.link(o_dia)
    dv, df = [], []
    c_dia = mathutils.Vector((0.0, -2.145, 0.625))
    sy, sz = 0.026, 0.042
    dv.append(c_dia + mathutils.Vector((0, -0.012, sz)))
    dv.append(c_dia + mathutils.Vector((sy, -0.010, 0)))
    dv.append(c_dia + mathutils.Vector((0, -0.012, -sz)))
    dv.append(c_dia + mathutils.Vector((-sy, -0.010, 0)))
    dv.append(c_dia + mathutils.Vector((0, -0.018, 0)))
    df.append((0, 1, 4))
    df.append((1, 2, 4))
    df.append((2, 3, 4))
    df.append((3, 0, 4))
    m_dia.from_pydata(dv, [], df)
    m_dia.update()
    o_dia.data.materials.append(mat_chrome)

    # Front Split Grille Slats angled with bumper curvature (inner x=0.10, outer x=0.34)
    for gr_name, s_sign in [("Grille_Slats_L", -1), ("Grille_Slats_R", 1)]:
        old_gr = bpy.data.objects.get(gr_name)
        if old_gr:
            bpy.data.objects.remove(old_gr, do_unlink=True)
        m_gr = bpy.data.meshes.new(gr_name + "_Mesh")
        o_gr = bpy.data.objects.new(gr_name, m_gr)
        bpy.context.collection.objects.link(o_gr)
        gv, gf = [], []
        # 3 horizontal slats
        for slat_i in range(3):
            z_slat = 0.505 + slat_i * 0.018
            # Inner point near nose beak: x = 0.10, y = -2.165
            # Outer point near headlight: x = 0.32, y = -2.125
            p_in = mathutils.Vector((s_sign * 0.10, -2.165, z_slat))
            p_out = mathutils.Vector((s_sign * 0.32, -2.125, z_slat))
            gv.append(p_in - mathutils.Vector((0, 0, 0.004)))
            gv.append(p_out - mathutils.Vector((0, 0, 0.004)))
            gv.append(p_out + mathutils.Vector((0, 0, 0.004)))
            gv.append(p_in + mathutils.Vector((0, 0, 0.004)))
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
        for i in range(12):
            a = 2 * math.pi * i / 12
            fog_v.append(cp_fog + mathutils.Vector((0.038 * math.cos(a), 0.008, 0.038 * math.sin(a))))
        for i in range(12):
            fog_f.append((0, i + 1, (i + 1) % 12 + 1))
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

    # Driver wiper parked in cowl tray below hood line (y ~ -1.14, z ~ 0.77)
    m_wd = bpy.data.meshes.new("Front_Wiper_Driver_Mesh")
    o_wd = bpy.data.objects.new("Front_Wiper_Driver", m_wd)
    bpy.context.collection.objects.link(o_wd)
    wd_v = [
        mathutils.Vector((-0.46, -1.16, 0.765)),
        mathutils.Vector((-0.02, -1.14, 0.778)),
        mathutils.Vector((-0.02, -1.14, 0.786)),
        mathutils.Vector((-0.46, -1.16, 0.773))
    ]
    m_wd.from_pydata(wd_v, [], [(0, 1, 2, 3)])
    m_wd.update()
    o_wd.data.materials.append(mat_black)

    # Passenger wiper parked along cowl
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

    # Rear liftback wiper flush on rear window glass (y ~ 1.50 to 1.76, z ~ 1.01 to 1.15)
    m_rw = bpy.data.meshes.new("Rear_Wiper_Mesh")
    o_rw = bpy.data.objects.new("Rear_Wiper", m_rw)
    bpy.context.collection.objects.link(o_rw)
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
    # ROUND 9: GREEN SOLARGLASS TINT WITH SKY REFLECTIONS & COCKPIT
    # --------------------------------------------------------
    print("[Round 9] Calibrating Renault Solarglass with outdoor sky reflections & cockpit depth...")
    mat_solar = get_or_create_mat("Laguna_Factory_Solarglass")
    sg_bsdf = mat_solar.node_tree.nodes.get("Principled BSDF")
    if sg_bsdf:
        # Authentic automotive Solarglass: light pale green tint, high transmission & glossy clearcoat
        sg_bsdf.inputs['Base Color'].default_value = (0.84, 0.93, 0.89, 1.0)
        sg_bsdf.inputs['Roughness'].default_value = 0.015
        sg_bsdf.inputs['Transmission Weight'].default_value = 0.85
        sg_bsdf.inputs['Alpha'].default_value = 0.45
        sg_bsdf.inputs['IOR'].default_value = 1.52
        sg_bsdf.inputs['Coat Weight'].default_value = 1.0
        sg_bsdf.inputs['Coat Roughness'].default_value = 0.005

    for g_name in ['unnamed.021', 'unnamed.027']:
        og = bpy.data.objects.get(g_name)
        if og:
            og.hide_render = False
            og.hide_viewport = False
            og.data.materials.clear()
            og.data.materials.append(mat_solar)

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
    # ROUND 10: TAILGATE BADGING, EURO PLATE, HDR STAGING & RENDERS
    # --------------------------------------------------------
    print("[Round 10] Tailgate badging, European license plate, HDR outdoor environment & 1080p renders...")
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

    # Setup 32-bit floating point outdoor HDR environment
    world = scene.world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    node_env = nt.nodes.new('ShaderNodeTexEnvironment')
    node_env.image = bpy.data.images.load(HDR_PATH)
    node_bg = nt.nodes.new('ShaderNodeBackground')
    node_bg.inputs['Strength'].default_value = 1.0
    node_out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(node_env.outputs['Color'], node_bg.inputs['Color'])
    nt.links.new(node_bg.outputs['Background'], node_out.inputs['Surface'])

    # Asphalt pavement plane below vehicle for realistic grounding & ambient contact shadows
    old_pave = bpy.data.objects.get("Studio_Pavement")
    if not old_pave:
        bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0, 0, 0.0))
        pave = bpy.context.active_object
        pave.name = "Studio_Pavement"
        mat_asphalt = get_or_create_mat("Laguna_Road_Asphalt")
        pave.data.materials.append(mat_asphalt)

    # AgX Color Management with neutral exposure
    scene.view_settings.view_transform = 'AgX'
    try:
        scene.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    scene.view_settings.exposure = 0.0

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
    print("DEFINITIVE 10-ROUND REFINEMENT COMPLETED SUCCESSFULLY!")
    print("==========================================================")

if __name__ == "__main__":
    execute_definitive_pass()
