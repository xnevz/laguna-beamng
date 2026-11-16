"""
build_pure_laguna2_masterpiece.py
=================================
Definitive 10-Phase Renault Laguna II (Phase 1/2) Transformation:
Crafts a 100% authentic Laguna II matching user reference photos:
  - Rear: media_1794832234562_fa418d5b.jpg (Algerian silver Laguna II: yellow plate 08976 102 44,
          twin-circle teardrop taillights, decklid bridge lip spoiler, upright tailgate diamond)
  - Front: media_1794832256808_767c597d.jpg (French silver Laguna II: plate 227 CDG 92,
           swept-back projector headlights, hood beak, split grilles, 17" Silverstone wheels)
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

def clear_old_procedural_objects():
    """Remove any previously created crude/distorted procedural objects"""
    procedural_names = [
        'Taillight_Laguna2_L', 'Taillight_Laguna2_R', 'Bridge_Spoiler_Laguna2',
        'Decklid_Surface', 'Headlight_Laguna2_L', 'Headlight_Laguna2_R',
        'Front_License_Plate', 'License_Plate', 'Front_Renault_Diamond',
        'Rear_Renault_Diamond', 'Grille_Slats_L', 'Grille_Slats_R',
        'Fog_Light_L', 'Fog_Light_R', 'Third_Brake_Light', 'Moulding_Door_FL',
        'Moulding_Door_FR', 'Moulding_Door_RL', 'Moulding_Door_RR',
        'Side_Repeater_L', 'Side_Repeater_R', 'Door_Handle_FL', 'Door_Handle_FR',
        'Door_Handle_RL', 'Door_Handle_RR', 'Wheel_Cap_FL', 'Wheel_Cap_FR',
        'Wheel_Cap_RL', 'Wheel_Cap_RR', 'Rear_Wiper', 'Roof_Antenna',
        'Studio_Pavement', 'Studio_Floor', 'Parcel_Shelf'
    ]
    for n in procedural_names:
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

def build_masterpiece():
    print("==========================================================")
    print("STARTING 10-PHASE DEFINITIVE RENAULT LAGUNA II REBUILD")
    print("==========================================================")
    scene = bpy.context.scene

    clear_old_procedural_objects()

    # --------------------------------------------------------
    # PHASE 1: UNIBODY & CHASSIS CLEAN FOUNDATION
    # --------------------------------------------------------
    print("[Phase 1] Configuring clean unibody and unhiding factory glass...")

    # Hide internal race cockpit & touring car clutter
    hidden_race_parts = [
        'unnamed.028', 'unnamed.029', 'unnamed.069', 'unnamed.135',
        'unnamed.136', 'unnamed.149', 'unnamed.150', 'unnamed.152',
        'unnamed.165', 'unnamed.168', 'unnamed.175', 'unnamed.190',
        'unnamed.194', 'unnamed.197', 'unnamed.213', 'unnamed.214',
        'unnamed.216', 'unnamed.225', 'unnamed.232', 'unnamed.239',
        'unnamed.031', 'unnamed.032', 'unnamed.033', 'unnamed.070', 'unnamed.071'
    ]
    for n in hidden_race_parts:
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = True
            o.hide_viewport = True

    # PBR Materials setup
    # 1. Authentic Renault Laguna II Gris Platine / Beige Poivre (B64) Metallic Clearcoat Paint
    mat_paint = get_or_create_mat("Laguna_Champagne_Silver")
    p_bsdf = mat_paint.node_tree.nodes.get("Principled BSDF")
    if p_bsdf:
        p_bsdf.inputs['Base Color'].default_value = (0.72, 0.71, 0.67, 1.0)
        p_bsdf.inputs['Metallic'].default_value = 0.78
        p_bsdf.inputs['Roughness'].default_value = 0.22
        p_bsdf.inputs['Coat Weight'].default_value = 1.0
        p_bsdf.inputs['Coat Roughness'].default_value = 0.03
        p_bsdf.inputs['Coat IOR'].default_value = 1.50

    # 2. Dark Charcoal Protective Rub Strips & Bumpers (Textured Automotive Polypropylene)
    mat_trim = get_or_create_mat("Laguna_Trim_Charcoal")
    tr_bsdf = mat_trim.node_tree.nodes.get("Principled BSDF")
    if tr_bsdf:
        tr_bsdf.inputs['Base Color'].default_value = (0.055, 0.055, 0.060, 1.0)
        tr_bsdf.inputs['Metallic'].default_value = 0.0
        tr_bsdf.inputs['Roughness'].default_value = 0.75

    # 3. Polished Renault Chrome
    mat_chrome = get_or_create_mat("Laguna_Chrome")
    ch_bsdf = mat_chrome.node_tree.nodes.get("Principled BSDF")
    if ch_bsdf:
        ch_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.96, 1.0)
        ch_bsdf.inputs['Metallic'].default_value = 0.98
        ch_bsdf.inputs['Roughness'].default_value = 0.04

    # 4. Solarglass Green Tint
    mat_glass = get_or_create_mat("Laguna_Factory_Solarglass")
    gl_bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
    if gl_bsdf:
        gl_bsdf.inputs['Base Color'].default_value = (0.84, 0.94, 0.89, 1.0)
        gl_bsdf.inputs['Roughness'].default_value = 0.01
        gl_bsdf.inputs['Alpha'].default_value = 0.35
        gl_bsdf.inputs['IOR'].default_value = 1.52
        gl_bsdf.inputs['Coat Weight'].default_value = 1.0
        gl_bsdf.inputs['Coat Roughness'].default_value = 0.01
    mat_glass.blend_method = 'BLEND'

    # Unibody setup
    o_004 = bpy.data.objects.get("unnamed.004")
    if o_004:
        o_004.hide_render = False
        o_004.hide_viewport = False
        o_004.data.materials.clear()
        o_004.data.materials.append(mat_paint)
        o_004.data.materials.append(mat_trim)

        # Assign dark charcoal trim to bumper rub strip faces
        for poly in o_004.data.polygons:
            poly_verts = [o_004.data.vertices[v_idx].co for v_idx in poly.vertices]
            poly_z = sum(v.z for v in poly_verts) / len(poly_verts)
            poly_y = sum(v.y for v in poly_verts) / len(poly_verts)
            # Rear bumper protective rub strip band (Z: 0.54 - 0.62, Y > 2.05)
            if poly_y > 2.05 and 0.54 <= poly_z <= 0.62:
                poly.material_index = 1
            # Front bumper protective rub strip band (Z: 0.43 - 0.51, Y < -2.00)
            elif poly_y < -2.00 and 0.43 <= poly_z <= 0.51:
                poly.material_index = 1
            else:
                poly.material_index = 0

    # Unhide all factory glass objects!
    glass_objects = [
        'unnamed.030', 'unnamed.155', 'unnamed.219', # Rear fastback glass
        'unnamed.164', 'unnamed.196', 'unnamed.238', # Windshield
        'unnamed.060', 'unnamed.066', 'unnamed.142', 'unnamed.148', # Front door glass
        'unnamed.170', 'unnamed.171', 'unnamed.172', # Rear left door & quarter glass
        'unnamed.177', 'unnamed.178', 'unnamed.179', # Rear right door & quarter glass
        'unnamed.227', 'unnamed.228', 'unnamed.229',
        'unnamed.234', 'unnamed.235', 'unnamed.236',
        'unnamed.243', 'unnamed.244', 'unnamed.245',
        'unnamed.249', 'unnamed.250', 'unnamed.251'
    ]
    for n in glass_objects:
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = False
            o.hide_viewport = False
            o.data.materials.clear()
            o.data.materials.append(mat_glass)

    # --------------------------------------------------------
    # PHASE 2: GENUINE LAGUNA II SWEPT-BACK PROJECTOR HEADLIGHTS
    # --------------------------------------------------------
    print("[Phase 2] Modeling authentic swept-back Laguna II projector headlights...")

    mat_hl_lens = get_or_create_mat("Laguna_Headlight_Glass")
    hl_bsdf = mat_hl_lens.node_tree.nodes.get("Principled BSDF")
    if hl_bsdf:
        hl_bsdf.inputs['Base Color'].default_value = (0.97, 0.98, 1.0, 1.0)
        hl_bsdf.inputs['Roughness'].default_value = 0.005
        hl_bsdf.inputs['Alpha'].default_value = 0.12
        hl_bsdf.inputs['IOR'].default_value = 1.55
        hl_bsdf.inputs['Coat Weight'].default_value = 1.0
        hl_bsdf.inputs['Coat Roughness'].default_value = 0.01
    mat_hl_lens.blend_method = 'BLEND'

    mat_hl_chrome = get_or_create_mat("Laguna_Headlight_Chrome")
    hc_bsdf = mat_hl_chrome.node_tree.nodes.get("Principled BSDF")
    if hc_bsdf:
        hc_bsdf.inputs['Base Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        hc_bsdf.inputs['Metallic'].default_value = 0.98
        hc_bsdf.inputs['Roughness'].default_value = 0.02
        hc_bsdf.inputs['Emission Color'].default_value = (0.95, 0.97, 1.0, 1.0)
        hc_bsdf.inputs['Emission Strength'].default_value = 0.35

    mat_amber = get_or_create_mat("Laguna_Amber_Indicator")
    am_bsdf = mat_amber.node_tree.nodes.get("Principled BSDF")
    if am_bsdf:
        am_bsdf.inputs['Base Color'].default_value = (0.98, 0.45, 0.02, 1.0)
        am_bsdf.inputs['Roughness'].default_value = 0.08
        am_bsdf.inputs['Alpha'].default_value = 0.85

    # Build aerodynamic swept-back headlights for Left and Right sides
    # Laguna II headlights follow the nose curvature from X=+/-0.42 to +/-0.77, Y=-2.12 to -1.90, Z=0.51 to 0.62
    for side, s_name in [(1, "L"), (-1, "R")]:
        mesh = bpy.data.meshes.new(f"Headlight_Laguna2_{s_name}")
        obj = bpy.data.objects.new(f"Headlight_Laguna2_{s_name}", mesh)
        bpy.context.collection.objects.link(obj)

        verts = []
        faces = []
        mat_indices = []

        # 1. Backing bowl / housing (sits flush inside fender cavity)
        # Inner corner (near grille): x=0.42, y=-2.12, z=0.55
        # Top-inner: x=0.46, y=-2.08, z=0.61
        # Top-outer (swept back): x=0.76, y=-1.92, z=0.61
        # Outer tip: x=0.78, y=-1.90, z=0.55
        # Bottom-outer: x=0.76, y=-1.92, z=0.51
        # Bottom-inner: x=0.44, y=-2.10, z=0.51
        def pt(x, y, z):
            return mathutils.Vector((side * x, y, z))

        # Base 6 contour points for back housing
        b_pts = [
            pt(0.42, -2.11, 0.55),
            pt(0.46, -2.07, 0.61),
            pt(0.76, -1.91, 0.61),
            pt(0.78, -1.89, 0.55),
            pt(0.76, -1.91, 0.51),
            pt(0.44, -2.09, 0.51),
        ]
        # Front 6 contour points for outer clear lens (slight outward curve)
        f_pts = [
            pt(0.42, -2.13, 0.55),
            pt(0.46, -2.09, 0.62),
            pt(0.77, -1.93, 0.62),
            pt(0.79, -1.91, 0.55),
            pt(0.77, -1.93, 0.51),
            pt(0.44, -2.11, 0.51),
        ]

        # Housing Backing
        v_offset = len(verts)
        verts.extend(b_pts)
        # Housing face (material 0: chrome reflector)
        faces.append((v_offset, v_offset+1, v_offset+2, v_offset+3))
        faces.append((v_offset, v_offset+3, v_offset+4, v_offset+5))
        mat_indices.extend([0, 0])

        # Outer Polycarbonate Lens
        l_offset = len(verts)
        verts.extend(f_pts)
        faces.append((l_offset, l_offset+1, l_offset+2, l_offset+3))
        faces.append((l_offset, l_offset+3, l_offset+4, l_offset+5))
        mat_indices.extend([1, 1]) # material 1: clear lens

        # Side walls connecting housing to lens
        for i in range(6):
            nxt = (i + 1) % 6
            faces.append((v_offset + i, v_offset + nxt, l_offset + nxt, l_offset + i))
            mat_indices.append(2) # material 2: dark trim border

        # 2. Chrome Projector Bulbs inside housing
        # Projector 1: Low beam projector (outer round unit, diameter 65mm)
        p1_center = pt(0.66, -1.97, 0.56)
        r_p1 = 0.032
        p1_base = len(verts)
        for ang_idx in range(12):
            ang = ang_idx * 2 * math.pi / 12
            verts.append(p1_center + mathutils.Vector((side * r_p1 * math.cos(ang), -0.015, r_p1 * math.sin(ang))))
        # Center peak of projector lens
        verts.append(p1_center + mathutils.Vector((0, -0.025, 0)))
        for i in range(12):
            nxt = (i + 1) % 12
            faces.append((p1_base + i, p1_base + nxt, p1_base + 12))
            mat_indices.append(0) # chrome projector

        # Projector 2: High beam reflector (inner round unit, diameter 60mm)
        p2_center = pt(0.53, -2.04, 0.56)
        r_p2 = 0.030
        p2_base = len(verts)
        for ang_idx in range(12):
            ang = ang_idx * 2 * math.pi / 12
            verts.append(p2_center + mathutils.Vector((side * r_p2 * math.cos(ang), -0.015, r_p2 * math.sin(ang))))
        verts.append(p2_center + mathutils.Vector((0, -0.025, 0)))
        for i in range(12):
            nxt = (i + 1) % 12
            faces.append((p2_base + i, p2_base + nxt, p2_base + 12))
            mat_indices.append(0) # chrome projector

        # Projector 3: Outer amber turn signal reflector
        p3_center = pt(0.74, -1.93, 0.55)
        p3_base = len(verts)
        r_p3 = 0.018
        for ang_idx in range(8):
            ang = ang_idx * 2 * math.pi / 8
            verts.append(p3_center + mathutils.Vector((side * r_p3 * math.cos(ang), -0.010, r_p3 * math.sin(ang))))
        verts.append(p3_center + mathutils.Vector((0, -0.018, 0)))
        for i in range(8):
            nxt = (i + 1) % 8
            faces.append((p3_base + i, p3_base + nxt, p3_base + 8))
            mat_indices.append(3) # amber indicator

        mesh.from_pydata(verts, [], faces)
        mesh.update()

        obj.data.materials.append(mat_hl_chrome) # slot 0
        obj.data.materials.append(mat_hl_lens)   # slot 1
        obj.data.materials.append(mat_trim)      # slot 2
        obj.data.materials.append(mat_amber)     # slot 3

        for f_idx, mat_id in enumerate(mat_indices):
            if f_idx < len(mesh.polygons):
                mesh.polygons[f_idx].material_index = mat_id

    # --------------------------------------------------------
    # PHASE 3: HOOD NOSE BEAK, SPLIT GRILLES, CHROME DIAMOND & FOG LIGHTS
    # --------------------------------------------------------
    print("[Phase 3] Modeling central hood nose beak, split grilles & fog lamps...")

    # Central Hood Nose Beak (smooth transition carrying the diamond between grilles)
    bm_beak = bmesh.new()
    # Beak geometry: X from -0.16 to +0.16, sloping down to Y=-2.16, Z=0.52 to 0.68
    bv0 = bm_beak.verts.new((-0.16, -2.06, 0.68))
    bv1 = bm_beak.verts.new((0.16, -2.06, 0.68))
    bv2 = bm_beak.verts.new((0.12, -2.16, 0.54))
    bv3 = bm_beak.verts.new((-0.12, -2.16, 0.54))
    bm_beak.faces.new((bv0, bv1, bv2, bv3))
    # Beak lower return
    bv4 = bm_beak.verts.new((-0.10, -2.15, 0.50))
    bv5 = bm_beak.verts.new((0.10, -2.15, 0.50))
    bm_beak.faces.new((bv3, bv2, bv5, bv4))
    mesh_beak = bpy.data.meshes.new("Hood_Nose_Beak")
    bm_beak.to_mesh(mesh_beak)
    bm_beak.free()
    obj_beak = bpy.data.objects.new("Hood_Nose_Beak", mesh_beak)
    bpy.context.collection.objects.link(obj_beak)
    obj_beak.data.materials.append(mat_paint)

    # 3D Chrome Renault Diamond Emblem on Beak (Upright centered at X=0, Y=-2.15, Z=0.61)
    bm_dia = bmesh.new()
    dv_top = bm_dia.verts.new((0.000, -2.155, 0.655))
    dv_right = bm_dia.verts.new((0.026, -2.150, 0.610))
    dv_bottom = bm_dia.verts.new((0.000, -2.145, 0.565))
    dv_left = bm_dia.verts.new((-0.026, -2.150, 0.610))
    dv_center = bm_dia.verts.new((0.000, -2.165, 0.610)) # 3D faceted center ridge
    bm_dia.faces.new((dv_top, dv_right, dv_center))
    bm_dia.faces.new((dv_right, dv_bottom, dv_center))
    bm_dia.faces.new((dv_bottom, dv_left, dv_center))
    bm_dia.faces.new((dv_left, dv_top, dv_center))
    mesh_dia = bpy.data.meshes.new("Front_Renault_Diamond")
    bm_dia.to_mesh(mesh_dia)
    bm_dia.free()
    obj_dia = bpy.data.objects.new("Front_Renault_Diamond", mesh_dia)
    bpy.context.collection.objects.link(obj_dia)
    obj_dia.data.materials.append(mat_chrome)

    # Laguna II Split Grilles (Flanking beak, between beak X=+/-0.13 and headlights X=+/-0.41)
    for side, s_name in [(1, "L"), (-1, "R")]:
        bm_grille = bmesh.new()
        gx_in = side * 0.14
        gx_out = side * 0.40
        gy = -2.12
        gz_top = 0.60
        gz_bot = 0.53
        # Recessed grille backing
        gv0 = bm_grille.verts.new((gx_in, gy, gz_top))
        gv1 = bm_grille.verts.new((gx_out, gy + 0.02, gz_top))
        gv2 = bm_grille.verts.new((gx_out, gy + 0.02, gz_bot))
        gv3 = bm_grille.verts.new((gx_in, gy, gz_bot))
        bm_grille.faces.new((gv0, gv1, gv2, gv3))
        # 2 Horizontal matte slats
        for slat_z in [0.575, 0.550]:
            sv0 = bm_grille.verts.new((gx_in, gy - 0.008, slat_z + 0.005))
            sv1 = bm_grille.verts.new((gx_out, gy + 0.012, slat_z + 0.005))
            sv2 = bm_grille.verts.new((gx_out, gy + 0.012, slat_z - 0.005))
            sv3 = bm_grille.verts.new((gx_in, gy - 0.008, slat_z - 0.005))
            bm_grille.faces.new((sv0, sv1, sv2, sv3))
        mesh_grille = bpy.data.meshes.new(f"Grille_Slats_{s_name}")
        bm_grille.to_mesh(mesh_grille)
        bm_grille.free()
        obj_grille = bpy.data.objects.new(f"Grille_Slats_{s_name}", mesh_grille)
        bpy.context.collection.objects.link(obj_grille)
        obj_grille.data.materials.append(mat_trim)

    # Front Circular Fog Lamps in Lower Bumper (at X=+/-0.62, Y=-2.12, Z=0.28)
    for side, s_name in [(1, "L"), (-1, "R")]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16, radius=0.038, depth=0.015,
            location=(side * 0.62, -2.12, 0.28),
            rotation=(math.radians(90), 0, 0)
        )
        fog = bpy.context.active_object
        fog.name = f"Fog_Light_{s_name}"
        fog.data.materials.append(mat_hl_lens)

    # Front European License Plate "227 CDG 92" matching media_1794832256808_767c597d.jpg
    mat_fplate = get_or_create_mat("Laguna_Front_Plate_White")
    fp_bsdf = mat_fplate.node_tree.nodes.get("Principled BSDF")
    if fp_bsdf:
        fp_bsdf.inputs['Base Color'].default_value = (0.92, 0.92, 0.94, 1.0)
        fp_bsdf.inputs['Roughness'].default_value = 0.25
        fp_bsdf.inputs['Coat Weight'].default_value = 0.8
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, -2.22, 0.36), rotation=(math.radians(90), 0, 0))
    fplate = bpy.context.active_object
    fplate.name = "Front_License_Plate"
    fplate.scale = (0.52, 0.11, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    fplate.data.materials.append(mat_fplate)

    # --------------------------------------------------------
    # PHASE 4: ICONIC LAGUNA II TWIN-CIRCLE TEARDROP TAILLIGHTS
    # --------------------------------------------------------
    print("[Phase 4] Modeling authentic Laguna II twin-circle teardrop taillight clusters...")

    mat_tail_ruby = get_or_create_mat("Laguna_Taillight_Ruby")
    tr_bsdf = mat_tail_ruby.node_tree.nodes.get("Principled BSDF")
    if tr_bsdf:
        tr_bsdf.inputs['Base Color'].default_value = (0.75, 0.02, 0.02, 1.0)
        tr_bsdf.inputs['Roughness'].default_value = 0.04
        tr_bsdf.inputs['Alpha'].default_value = 0.78
        tr_bsdf.inputs['Transmission Weight'].default_value = 0.25
        tr_bsdf.inputs['Coat Weight'].default_value = 1.0
        tr_bsdf.inputs['Coat Roughness'].default_value = 0.01
    mat_tail_ruby.blend_method = 'BLEND'

    mat_tail_pupil = get_or_create_mat("Laguna_Taillight_Pupil")
    tp_bsdf = mat_tail_pupil.node_tree.nodes.get("Principled BSDF")
    if tp_bsdf:
        tp_bsdf.inputs['Base Color'].default_value = (0.92, 0.92, 0.95, 1.0)
        tp_bsdf.inputs['Metallic'].default_value = 0.95
        tp_bsdf.inputs['Roughness'].default_value = 0.08
        tp_bsdf.inputs['Emission Color'].default_value = (0.90, 0.15, 0.15, 1.0)
        tp_bsdf.inputs['Emission Strength'].default_value = 0.40

    # Build Left and Right authentic Laguna II teardrop taillights
    # Matching user rear reference photo media_1794832234562_fa418d5b.jpg:
    # Outer bounds: X from +/-0.28 (trunk seam) to +/-0.76 (quarter panel outer wraparound)
    # Height: Z from 0.70 to 0.81. Y from 2.08 to 2.14.
    for side, s_name in [(1, "L"), (-1, "R")]:
        mesh_t = bpy.data.meshes.new(f"Taillight_Laguna2_{s_name}")
        obj_t = bpy.data.objects.new(f"Taillight_Laguna2_{s_name}", mesh_t)
        bpy.context.collection.objects.link(obj_t)

        tv = []
        tf = []
        tm = []

        # Teardrop contour:
        # Inner-most point (near center trunk): x=0.28, y=2.135, z=0.755
        # Top-inner: x=0.36, y=2.130, z=0.795
        # Top-middle: x=0.55, y=2.115, z=0.805
        # Top-outer (wraparound): x=0.75, y=2.085, z=0.785
        # Outer-most tip: x=0.77, y=2.075, z=0.755
        # Bottom-outer: x=0.75, y=2.085, z=0.720
        # Bottom-middle: x=0.55, y=2.115, z=0.710
        # Bottom-inner: x=0.36, y=2.130, z=0.720
        def tpt(x, y, z):
            return mathutils.Vector((side * x, y, z))

        t_poly = [
            tpt(0.28, 2.135, 0.755),
            tpt(0.36, 2.130, 0.795),
            tpt(0.55, 2.115, 0.805),
            tpt(0.75, 2.085, 0.785),
            tpt(0.77, 2.075, 0.755),
            tpt(0.75, 2.085, 0.720),
            tpt(0.55, 2.115, 0.710),
            tpt(0.36, 2.130, 0.720),
        ]
        # Outer ruby polycarbonate lens
        base_v = len(tv)
        tv.extend(t_poly)
        # Quads covering teardrop face
        tf.append((base_v, base_v+1, base_v+6, base_v+7))
        tf.append((base_v+1, base_v+2, base_v+5, base_v+6))
        tf.append((base_v+2, base_v+3, base_v+4, base_v+5))
        tm.extend([0, 0, 0]) # ruby lens

        # Two Iconic Circular Chrome Pupils inside each cluster:
        # Pupil 1: Outer circular brake/tail lamp (centered at X=0.63, Y=2.095, Z=0.755)
        c1 = tpt(0.63, 2.095, 0.755)
        r_c1 = 0.032
        p1_idx = len(tv)
        for i in range(12):
            ang = i * 2 * math.pi / 12
            tv.append(c1 + mathutils.Vector((side * r_c1 * math.cos(ang), -0.005, r_c1 * math.sin(ang))))
        tv.append(c1 + mathutils.Vector((0, 0.008, 0))) # central convex bulb
        for i in range(12):
            nxt = (i + 1) % 12
            tf.append((p1_idx + i, p1_idx + nxt, p1_idx + 12))
            tm.append(1) # chrome/pupil material

        # Pupil 2: Inner circular reverse/indicator lamp (centered at X=0.45, Y=2.120, Z=0.755)
        c2 = tpt(0.45, 2.120, 0.755)
        r_c2 = 0.030
        p2_idx = len(tv)
        for i in range(12):
            ang = i * 2 * math.pi / 12
            tv.append(c2 + mathutils.Vector((side * r_c2 * math.cos(ang), -0.005, r_c2 * math.sin(ang))))
        tv.append(c2 + mathutils.Vector((0, 0.008, 0)))
        for i in range(12):
            nxt = (i + 1) % 12
            tf.append((p2_idx + i, p2_idx + nxt, p2_idx + 12))
            tm.append(1) # chrome/pupil material

        mesh_t.from_pydata(tv, [], tf)
        mesh_t.update()

        obj_t.data.materials.append(mat_tail_ruby)  # slot 0
        obj_t.data.materials.append(mat_tail_pupil) # slot 1

        for f_idx, mat_id in enumerate(tm):
            if f_idx < len(mesh_t.polygons):
                mesh_t.polygons[f_idx].material_index = mat_id

    # --------------------------------------------------------
    # PHASE 5: FACTORY LAGUNA II BRIDGE LIP SPOILER & 3RD BRAKE LIGHT
    # --------------------------------------------------------
    print("[Phase 5] Modeling genuine Laguna II decklid bridge spoiler & 3rd brake light...")

    # The factory Laguna II bridge spoiler spans across the trunk lid between X = -0.58 and +0.58.
    # It sits atop two streamlined side pedestals at X=+/-0.52, leaving a narrow horizontal air slot.
    bm_sp = bmesh.new()
    # Upper wing profile
    sp_w = 0.58
    sp_y_front = 2.02
    sp_y_rear = 2.08
    sp_z_top = 0.925
    sp_z_bot = 0.910
    # Wing aerofoil cross-section from -sp_w to +sp_w
    w_v0 = bm_sp.verts.new((-sp_w, sp_y_front, sp_z_top))
    w_v1 = bm_sp.verts.new((sp_w, sp_y_front, sp_z_top))
    w_v2 = bm_sp.verts.new((sp_w, sp_y_rear, sp_z_top))
    w_v3 = bm_sp.verts.new((-sp_w, sp_y_rear, sp_z_top))
    bm_sp.faces.new((w_v0, w_v1, w_v2, w_v3)) # top face

    w_b0 = bm_sp.verts.new((-sp_w, sp_y_front, sp_z_bot))
    w_b1 = bm_sp.verts.new((sp_w, sp_y_front, sp_z_bot))
    w_b2 = bm_sp.verts.new((sp_w, sp_y_rear, sp_z_bot))
    w_b3 = bm_sp.verts.new((-sp_w, sp_y_rear, sp_z_bot))
    bm_sp.faces.new((w_b3, w_b2, w_b1, w_b0)) # bottom face

    # Trailing and leading edges
    bm_sp.faces.new((w_v3, w_v2, w_b2, w_b3)) # rear edge
    bm_sp.faces.new((w_v0, w_b0, w_b1, w_v1)) # front edge
    bm_sp.faces.new((w_v0, w_v3, w_b3, w_b0)) # left endcap
    bm_sp.faces.new((w_v1, w_b1, w_b2, w_v2)) # right endcap

    # Two streamlined mounting pedestals connecting wing to decklid (at X=+/-0.50)
    for p_side in [1, -1]:
        px = p_side * 0.50
        pv0 = bm_sp.verts.new((px - 0.025, 2.03, 0.910))
        pv1 = bm_sp.verts.new((px + 0.025, 2.03, 0.910))
        pv2 = bm_sp.verts.new((px + 0.025, 2.07, 0.910))
        pv3 = bm_sp.verts.new((px - 0.025, 2.07, 0.910))

        pb0 = bm_sp.verts.new((px - 0.025, 2.03, 0.885))
        pb1 = bm_sp.verts.new((px + 0.025, 2.03, 0.885))
        pb2 = bm_sp.verts.new((px + 0.025, 2.07, 0.885))
        pb3 = bm_sp.verts.new((px - 0.025, 2.07, 0.885))

        bm_sp.faces.new((pv0, pb0, pb1, pv1))
        bm_sp.faces.new((pv1, pb1, pb2, pv2))
        bm_sp.faces.new((pv2, pb2, pb3, pv3))
        bm_sp.faces.new((pv3, pb3, pb0, pv0))

    mesh_sp = bpy.data.meshes.new("Bridge_Spoiler_Laguna2")
    bm_sp.to_mesh(mesh_sp)
    bm_sp.free()
    obj_sp = bpy.data.objects.new("Bridge_Spoiler_Laguna2", mesh_sp)
    bpy.context.collection.objects.link(obj_sp)
    obj_sp.data.materials.append(mat_paint)

    # High-mount slim horizontal LED 3rd Brake Light (Centered directly underneath bridge spoiler)
    mat_3rd_led = get_or_create_mat("Laguna_3rd_Brake_LED")
    led_bsdf = mat_3rd_led.node_tree.nodes.get("Principled BSDF")
    if led_bsdf:
        led_bsdf.inputs['Base Color'].default_value = (0.85, 0.02, 0.02, 1.0)
        led_bsdf.inputs['Roughness'].default_value = 0.10
        led_bsdf.inputs['Emission Color'].default_value = (0.95, 0.05, 0.05, 1.0)
        led_bsdf.inputs['Emission Strength'].default_value = 0.50

    bm_3rd = bmesh.new()
    # 30 cm wide x 1.6 cm high slim red strip flush on decklid at Z=0.875, Y=2.07
    b3_v0 = bm_3rd.verts.new((-0.15, 2.072, 0.883))
    b3_v1 = bm_3rd.verts.new((0.15, 2.072, 0.883))
    b3_v2 = bm_3rd.verts.new((0.15, 2.072, 0.867))
    b3_v3 = bm_3rd.verts.new((-0.15, 2.072, 0.867))
    bm_3rd.faces.new((b3_v0, b3_v1, b3_v2, b3_v3))
    mesh_3rd = bpy.data.meshes.new("Third_Brake_Light")
    bm_3rd.to_mesh(mesh_3rd)
    bm_3rd.free()
    obj_3rd = bpy.data.objects.new("Third_Brake_Light", mesh_3rd)
    bpy.context.collection.objects.link(obj_3rd)
    obj_3rd.data.materials.append(mat_3rd_led)

    # --------------------------------------------------------
    # PHASE 6: TAILGATE DIAMOND PLAQUE & ALGERIAN YELLOW LICENSE PLATE
    # --------------------------------------------------------
    print("[Phase 6] Modeling upright Renault diamond plaque & Algerian yellow license plate...")

    # Upright Tailgate Diamond Plaque (Centered vertically on tailgate at X=0, Y=2.138, Z=0.765)
    bm_plaque = bmesh.new()
    # Trapezoidal silver mounting plaque
    pq_v0 = bm_plaque.verts.new((-0.038, 2.136, 0.815))
    pq_v1 = bm_plaque.verts.new((0.038, 2.136, 0.815))
    pq_v2 = bm_plaque.verts.new((0.032, 2.138, 0.720))
    pq_v3 = bm_plaque.verts.new((-0.032, 2.138, 0.720))
    bm_plaque.faces.new((pq_v0, pq_v1, pq_v2, pq_v3))
    # 3D Chrome Diamond on top of plaque
    rd_top = bm_plaque.verts.new((0.000, 2.144, 0.800))
    rd_right = bm_plaque.verts.new((0.024, 2.144, 0.765))
    rd_bottom = bm_plaque.verts.new((0.000, 2.144, 0.730))
    rd_left = bm_plaque.verts.new((-0.024, 2.144, 0.765))
    rd_center = bm_plaque.verts.new((0.000, 2.152, 0.765)) # raised ridge
    bm_plaque.faces.new((rd_top, rd_right, rd_center))
    bm_plaque.faces.new((rd_right, rd_bottom, rd_center))
    bm_plaque.faces.new((rd_bottom, rd_left, rd_center))
    bm_plaque.faces.new((rd_left, rd_top, rd_center))

    mesh_plaque = bpy.data.meshes.new("Rear_Renault_Diamond")
    bm_plaque.to_mesh(mesh_plaque)
    bm_plaque.free()
    obj_plaque = bpy.data.objects.new("Rear_Renault_Diamond", mesh_plaque)
    bpy.context.collection.objects.link(obj_plaque)
    obj_plaque.data.materials.append(mat_chrome)

    # Algerian Yellow License Plate (08976 102 44) matching media_1794832234562_fa418d5b.jpg
    mat_plate_yellow = get_or_create_mat("Laguna_Rear_Plate_Yellow")
    py_bsdf = mat_plate_yellow.node_tree.nodes.get("Principled BSDF")
    if py_bsdf:
        # Authentic Algerian reflective yellow
        py_bsdf.inputs['Base Color'].default_value = (0.95, 0.76, 0.05, 1.0)
        py_bsdf.inputs['Roughness'].default_value = 0.22
        py_bsdf.inputs['Coat Weight'].default_value = 0.85

    # Recessed bumper license plate pocket: X=0, Y=2.22, Z=0.45
    bpy.ops.mesh.primitive_plane_add(
        size=1.0, location=(0, 2.220, 0.455),
        rotation=(math.radians(-90), 0, math.radians(180))
    )
    plate = bpy.context.active_object
    plate.name = "License_Plate"
    plate.scale = (0.52, 0.115, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    plate.data.materials.append(mat_plate_yellow)

    # --------------------------------------------------------
    # PHASE 7: FASTBACK SOLARGLASS, ROOF ANTENNA, PARCEL SHELF & REAR WIPER
    # --------------------------------------------------------
    print("[Phase 7] Configuring greenhouse details, antenna, parcel shelf & rear wiper...")

    # Sleek roof whip antenna at rear roof centerline (X=0, Y=1.22, Z=1.38, angled 55 degrees)
    bm_ant = bmesh.new()
    # Antenna base pod
    ab_v0 = bm_ant.verts.new((-0.015, 1.20, 1.378))
    ab_v1 = bm_ant.verts.new((0.015, 1.20, 1.378))
    ab_v2 = bm_ant.verts.new((0.012, 1.25, 1.375))
    ab_v3 = bm_ant.verts.new((-0.012, 1.25, 1.375))
    bm_ant.faces.new((ab_v0, ab_v1, ab_v2, ab_v3))
    # Flexible antenna mast extending backwards
    am_v0 = bm_ant.verts.new((0.000, 1.22, 1.385))
    am_v1 = bm_ant.verts.new((0.000, 1.40, 1.485))
    bm_ant.edges.new((am_v0, am_v1))
    mesh_ant = bpy.data.meshes.new("Roof_Antenna")
    bm_ant.to_mesh(mesh_ant)
    bm_ant.free()
    obj_ant = bpy.data.objects.new("Roof_Antenna", mesh_ant)
    bpy.context.collection.objects.link(obj_ant)
    obj_ant.data.materials.append(mat_trim)

    # Rear Window Wiper (Parked horizontally at bottom of fastback glass at Y=1.91, Z=0.91)
    bm_wip = bmesh.new()
    # Pivot at right of centerline, blade spanning left
    wp_v0 = bm_wip.verts.new((0.08, 1.90, 0.905))
    wp_v1 = bm_wip.verts.new((-0.38, 1.90, 0.910))
    bm_wip.edges.new((wp_v0, wp_v1))
    mesh_wip = bpy.data.meshes.new("Rear_Wiper")
    bm_wip.to_mesh(mesh_wip)
    bm_wip.free()
    obj_wip = bpy.data.objects.new("Rear_Wiper", mesh_wip)
    bpy.context.collection.objects.link(obj_wip)
    obj_wip.data.materials.append(mat_trim)

    # Carpeted interior rear parcel shelf (eliminates hollow see-through interior look)
    mat_shelf = get_or_create_mat("Laguna_Interior_Charcoal")
    sh_bsdf = mat_shelf.node_tree.nodes.get("Principled BSDF")
    if sh_bsdf:
        sh_bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.045, 1.0)
        sh_bsdf.inputs['Roughness'].default_value = 0.90
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 1.45, 0.78))
    shelf = bpy.context.active_object
    shelf.name = "Parcel_Shelf"
    shelf.scale = (1.18, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    shelf.data.materials.append(mat_shelf)

    # --------------------------------------------------------
    # PHASE 8: FLANK DETAILS: CONTINUOUS RUB STRIPS, PULL HANDLES & AMBER REPEATERS
    # --------------------------------------------------------
    print("[Phase 8] Modeling door protective rub strips, pull handles & amber side repeaters...")

    # Door protective rub strips running along the door swage lines
    # Front door: Y from -0.85 to -0.15, Z=0.54
    # Rear door: Y from -0.10 to +0.62, Z=0.54
    for side, s_name in [(1, "L"), (-1, "R")]:
        sx = side * 0.825
        # Front door rub strip
        bm_d1 = bmesh.new()
        f1_0 = bm_d1.verts.new((sx, -0.85, 0.56))
        f1_1 = bm_d1.verts.new((sx, -0.15, 0.56))
        f1_2 = bm_d1.verts.new((sx, -0.15, 0.52))
        f1_3 = bm_d1.verts.new((sx, -0.85, 0.52))
        bm_d1.faces.new((f1_0, f1_1, f1_2, f1_3))
        m_d1 = bpy.data.meshes.new(f"Moulding_Door_F{s_name}")
        bm_d1.to_mesh(m_d1)
        bm_d1.free()
        o_d1 = bpy.data.objects.new(f"Moulding_Door_F{s_name}", m_d1)
        bpy.context.collection.objects.link(o_d1)
        o_d1.data.materials.append(mat_trim)

        # Rear door rub strip
        bm_d2 = bmesh.new()
        f2_0 = bm_d2.verts.new((sx, -0.10, 0.56))
        f2_1 = bm_d2.verts.new((sx, 0.62, 0.56))
        f2_2 = bm_d2.verts.new((sx, 0.62, 0.52))
        f2_3 = bm_d2.verts.new((sx, -0.10, 0.52))
        bm_d2.faces.new((f2_0, f2_1, f2_2, f2_3))
        m_d2 = bpy.data.meshes.new(f"Moulding_Door_R{s_name}")
        bm_d2.to_mesh(m_d2)
        bm_d2.free()
        o_d2 = bpy.data.objects.new(f"Moulding_Door_R{s_name}", m_d2)
        bpy.context.collection.objects.link(o_d2)
        o_d2.data.materials.append(mat_trim)

        # Aerodynamic Pull Door Handles
        for door_y, d_label in [(-0.35, "F"), (0.40, "R")]:
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=0.024, location=(side * 0.835, door_y, 0.66)
            )
            hnd = bpy.context.active_object
            hnd.name = f"Door_Handle_{d_label}{s_name}"
            hnd.scale = (0.35, 2.2, 0.55)
            bpy.ops.object.transform_apply(scale=True)
            hnd.data.materials.append(mat_paint)

        # Amber Side Turn Repeater on Front Fender (at X=+/-0.83, Y=-1.45, Z=0.55)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=12, radius=0.012, depth=0.005,
            location=(side * 0.830, -1.45, 0.55),
            rotation=(0, math.radians(90), 0)
        )
        rep = bpy.context.active_object
        rep.name = f"Side_Repeater_{s_name}"
        rep.scale = (1.0, 1.8, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        rep.data.materials.append(mat_amber)

    # --------------------------------------------------------
    # PHASE 9: AUTHENTIC 17" RENAULT "SILVERSTONE" ALLOY WHEELS
    # --------------------------------------------------------
    print("[Phase 9] Modeling 17-spoke Renault Silverstone alloy wheels...")

    mat_alloy = get_or_create_mat("Laguna_Alloy_Silverstone")
    al_bsdf = mat_alloy.node_tree.nodes.get("Principled BSDF")
    if al_bsdf:
        al_bsdf.inputs['Base Color'].default_value = (0.86, 0.86, 0.88, 1.0)
        al_bsdf.inputs['Metallic'].default_value = 0.90
        al_bsdf.inputs['Roughness'].default_value = 0.12
        al_bsdf.inputs['Coat Weight'].default_value = 0.80

    mat_cavity = get_or_create_mat("Laguna_Wheel_Cavity_Dark")
    cv_bsdf = mat_cavity.node_tree.nodes.get("Principled BSDF")
    if cv_bsdf:
        cv_bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.045, 1.0)
        cv_bsdf.inputs['Metallic'].default_value = 0.20
        cv_bsdf.inputs['Roughness'].default_value = 0.65

    # 4 Wheel Hub Centers: Front Left, Front Right, Rear Left, Rear Right
    wheel_positions = [
        (mathutils.Vector((0.76, -1.33, 0.32)), 1, "FL"),
        (mathutils.Vector((-0.76, -1.33, 0.32)), -1, "FR"),
        (mathutils.Vector((0.76, 1.34, 0.32)), 1, "RL"),
        (mathutils.Vector((-0.76, 1.34, 0.32)), -1, "RR")
    ]

    for cp, side, w_name in wheel_positions:
        m_w = bpy.data.meshes.new(f"Wheel_Cap_{w_name}")
        o_w = bpy.data.objects.new(f"Wheel_Cap_{w_name}", m_w)
        bpy.context.collection.objects.link(o_w)

        wv = []
        wf = []
        m_slots = []

        # Dark cavity backing disk
        disk_start = len(wv)
        r_outer = 0.235 # 17-inch rim radius ~ 215-235mm
        for i in range(24):
            ang = i * 2 * math.pi / 24
            wv.append(mathutils.Vector((cp.x + side * 0.002, cp.y + r_outer * math.cos(ang), cp.z + r_outer * math.sin(ang))))
        wv.append(mathutils.Vector((cp.x + side * 0.002, cp.y, cp.z))) # center
        for i in range(24):
            nxt = (i + 1) % 24
            wf.append((disk_start + i, disk_start + nxt, disk_start + 24))
            m_slots.append((len(wf)-1, 2)) # dark cavity

        # Outer Bright Silver Rim Lip
        rim_start = len(wv)
        for i in range(24):
            ang = i * 2 * math.pi / 24
            wv.append(mathutils.Vector((cp.x + side * 0.010, cp.y + r_outer * math.cos(ang), cp.z + r_outer * math.sin(ang))))
            wv.append(mathutils.Vector((cp.x + side * 0.010, cp.y + (r_outer - 0.015) * math.cos(ang), cp.z + (r_outer - 0.015) * math.sin(ang))))
        for i in range(24):
            nxt = (i + 1) % 24
            wf.append((rim_start + 2*i, rim_start + 2*nxt, rim_start + 2*nxt + 1, rim_start + 2*i + 1))
            m_slots.append((len(wf)-1, 0)) # silver alloy

        # 17 Slim Radiating Spokes (Iconic Silverstone Design)
        r_hub = 0.065
        for s_idx in range(17):
            ang = s_idx * 2 * math.pi / 17
            half_w = 0.0055
            tang_y = -math.sin(ang) * half_w
            tang_z = math.cos(ang) * half_w
            rad_y = math.cos(ang)
            rad_z = math.sin(ang)

            spoke_start = len(wv)
            wv.append(mathutils.Vector((cp.x + side * 0.008, cp.y + r_hub * rad_y - tang_y, cp.z + r_hub * rad_z - tang_z)))
            wv.append(mathutils.Vector((cp.x + side * 0.008, cp.y + r_hub * rad_y + tang_y, cp.z + r_hub * rad_z + tang_z)))
            wv.append(mathutils.Vector((cp.x + side * 0.010, cp.y + (r_outer - 0.015) * rad_y + tang_y, cp.z + (r_outer - 0.015) * rad_z + tang_z)))
            wv.append(mathutils.Vector((cp.x + side * 0.010, cp.y + (r_outer - 0.015) * rad_y - tang_y, cp.z + (r_outer - 0.015) * rad_z - tang_z)))
            wf.append((spoke_start, spoke_start + 1, spoke_start + 2, spoke_start + 3))
            m_slots.append((len(wf)-1, 0)) # silver alloy

        # Center Chrome Diamond Emblem
        d_start = len(wv)
        dx = cp.x + side * 0.012
        sy, sz = 0.016, 0.024
        wv.append(mathutils.Vector((dx, cp.y, cp.z + sz)))
        wv.append(mathutils.Vector((dx, cp.y + sy, cp.z)))
        wv.append(mathutils.Vector((dx, cp.y, cp.z - sz)))
        wv.append(mathutils.Vector((dx, cp.y - sy, cp.z)))
        wf.append((d_start, d_start + 1, d_start + 2, d_start + 3))
        m_slots.append((len(wf)-1, 1)) # chrome

        m_w.from_pydata(wv, [], wf)
        m_w.update()
        o_w.data.materials.append(mat_alloy)
        o_w.data.materials.append(mat_chrome)
        o_w.data.materials.append(mat_cavity)
        for f_idx, mat_id in m_slots:
            if f_idx < len(m_w.polygons):
                m_w.polygons[f_idx].material_index = mat_id

    # --------------------------------------------------------
    # PHASE 10: CALIBRATED LIGHTING, ASPHALT GROUND & 1080P RENDERS
    # --------------------------------------------------------
    print("[Phase 10] Staging outdoor lighting, asphalt roadway & rendering 1080p images...")

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

    # Asphalt pavement plane below vehicle for realistic ground shadows
    old_pave = bpy.data.objects.get("Studio_Pavement")
    if not old_pave:
        bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0, 0, 0.0))
        pave = bpy.context.active_object
        pave.name = "Studio_Pavement"
        mat_asphalt = get_or_create_mat("Laguna_Road_Asphalt")
        as_bsdf = mat_asphalt.node_tree.nodes.get("Principled BSDF")
        if as_bsdf:
            as_bsdf.inputs['Base Color'].default_value = (0.16, 0.16, 0.17, 1.0)
            as_bsdf.inputs['Roughness'].default_value = 0.85
        pave.data.materials.append(mat_asphalt)

    # AgX Color Management with neutral exposure
    scene.view_settings.view_transform = 'AgX'
    try:
        scene.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    scene.view_settings.exposure = 0.0

    # Save updated master blend file
    blend_path = os.path.abspath(r"blender\laguna_master.blend")
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"[Phase 10] Saved updated master blend file: {blend_path}")

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

    # Front 3/4 Render matching media_1794832256808_767c597d.jpg
    print("[Phase 10] Rendering Front 3/4 validation angle...")
    cam.location = mathutils.Vector((-4.30, -4.40, 1.20))
    target_front = mathutils.Vector((0.0, -0.60, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear Angle matching media_1794832234562_fa418d5b.jpg
    print("[Phase 10] Rendering Rear validation angle...")
    cam.location = mathutils.Vector((0.00, 4.80, 0.85)) # Direct rear view matching the photo!
    target_rear = mathutils.Vector((0.0, 0.00, 0.72))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    # Synchronize presentation artifacts
    shutil.copy2(out_front, out_pres)
    shutil.copy2(out_front, os.path.join(ARTIFACT_DIR, "laguna_front.png"))
    shutil.copy2(out_rear, os.path.join(ARTIFACT_DIR, "laguna_rear.png"))
    shutil.copy2(out_pres, os.path.join(ARTIFACT_DIR, "laguna_presentation.png"))

    print("==========================================================")
    print("10-PHASE PURE LAGUNA II MASTERPIECE COMPLETED!")
    print("==========================================================")

if __name__ == "__main__":
    build_masterpiece()
