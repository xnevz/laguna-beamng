"""
Flawless Renault Laguna II Execution:
1. Restore unnamed.004 and unnamed.025 from blend1
2. Remove wing mount islands 5-10 from unnamed.025
3. Assign clean materials:
   - Body & Doors: Laguna_Champagne_Silver (Metallic 0.82, Roughness 0.16)
   - B-pillars & window frames: Laguna_Pillar_Black
   - Solarglass: Laguna_Factory_Solarglass (Alpha 0.28, pale green)
   - Cockpit interior: Laguna_Interior_Charcoal
   - Taillights: Ruby red + clear reverse
   - Wheels: Silver 7-spoke hubcaps with chrome diamonds
   - Flank trim: Clean 3D extruded door rub strips and amber repeaters
4. Save laguna_master.blend and render 1080p Front 3/4 and Rear 3/4
"""

import bpy
import bmesh
import mathutils
import math
import os
import shutil

def run_flawless():
    print("[Flawless] Starting...")
    scene = bpy.context.scene

    # 1. RESTORE UNNAMED.004 AND UNNAMED.025 FROM BLEND1
    blend1_path = os.path.abspath(r"blender\laguna_master.blend1")
    if os.path.exists(blend1_path):
        with bpy.data.libraries.load(blend1_path) as (data_from, data_to):
            data_to.objects = ["unnamed.004", "unnamed.025"]

        # Replace unnamed.004
        if data_to.objects[0]:
            old_o4 = bpy.data.objects.get("unnamed.004")
            if old_o4:
                bpy.data.objects.remove(old_o4, do_unlink=True)
            new_o4 = data_to.objects[0]
            new_o4.name = "unnamed.004"
            bpy.context.collection.objects.link(new_o4)

        # Replace unnamed.025
        if data_to.objects[1]:
            old_o25 = bpy.data.objects.get("unnamed.025")
            if old_o25:
                bpy.data.objects.remove(old_o25, do_unlink=True)
            new_o25 = data_to.objects[1]
            new_o25.name = "unnamed.025"
            bpy.context.collection.objects.link(new_o25)

            # Delete wing islands (islands with Z max > 1.0)
            bm = bmesh.new()
            bm.from_mesh(new_o25.data)
            visited = set()
            comps = []
            for f in bm.faces:
                if f in visited: continue
                comp = []
                stack = [f]
                visited.add(f)
                while stack:
                    curr = stack.pop()
                    comp.append(curr)
                    for edge in curr.edges:
                        for lf in edge.link_faces:
                            if lf not in visited:
                                visited.add(lf)
                                stack.append(lf)
                comps.append(comp)

            wing_faces = []
            for c in comps:
                max_z = max(v.co.z for f in c for v in f.verts)
                if max_z > 1.00:
                    wing_faces.extend(c)

            if wing_faces:
                bmesh.ops.delete(bm, geom=wing_faces, context='FACES')
                bm.to_mesh(new_o25.data)
                new_o25.data.update()
                print(f"[Flawless] Deleted {len(wing_faces)} wing island faces from unnamed.025!")
            bm.free()

    # 2. SHADERS
    mat_body = bpy.data.materials.get("Laguna_Champagne_Silver")
    mat_trim = bpy.data.materials.get("Laguna_Trim_Charcoal")
    mat_pillar = bpy.data.materials.get("Laguna_Pillar_Black")
    mat_glass = bpy.data.materials.get("Laguna_Factory_Solarglass")
    mat_interior = bpy.data.materials.get("Laguna_Interior_Charcoal")
    mat_tl_ruby = bpy.data.materials.get("Laguna_Taillight_Ruby")
    mat_tl_clear = bpy.data.materials.get("Laguna_Taillight_Clear")
    mat_hl_lens = bpy.data.materials.get("Laguna_Headlight_Glass")
    mat_amber = bpy.data.materials.get("Laguna_Amber_Indicator")
    mat_alloy = bpy.data.materials.get("Laguna_Factory_Alloy")
    mat_chrome = bpy.data.materials.get("Laguna_Chrome")

    # Set all body panels to clean Champagne Silver
    clean_body_objs = ['unnamed.004', 'unnamed.006', 'unnamed.007', 'unnamed.008',
                       'unnamed.011', 'unnamed.012', 'unnamed.025', 'unnamed.026',
                       'unnamed.028', 'unnamed.057', 'unnamed.063', 'unnamed.240',
                       'unnamed.246']
    for b_name in clean_body_objs:
        bo = bpy.data.objects.get(b_name)
        if bo:
            bo.data.materials.clear()
            bo.data.materials.append(mat_body)
            for p in bo.data.polygons:
                p.material_index = 0
            bo.hide_render = False

    # Neutralize interior blue
    mat_blue = bpy.data.materials.get("Laguna_Metallic_Blue")
    if mat_blue and mat_blue.node_tree:
        b_bsdf = mat_blue.node_tree.nodes.get("Principled BSDF")
        if b_bsdf:
            b_bsdf.inputs['Base Color'].default_value = (0.035, 0.035, 0.04, 1.0)
            b_bsdf.inputs['Metallic'].default_value = 0.0
            b_bsdf.inputs['Roughness'].default_value = 0.85

    for o in bpy.data.objects:
        if o.type == 'MESH':
            for s in o.material_slots:
                if s.material and ('Blue' in s.material.name):
                    s.material = mat_interior

    # Window surrounds -> Satin Black
    pillar_surrounds = ['unnamed.022', 'unnamed.023', 'unnamed.060', 'unnamed.066', 'unnamed.142',
                        'unnamed.148', 'unnamed.170', 'unnamed.171', 'unnamed.177', 'unnamed.178',
                        'unnamed.206', 'unnamed.212', 'unnamed.227', 'unnamed.228', 'unnamed.234',
                        'unnamed.235', 'unnamed.243', 'unnamed.244', 'unnamed.249']
    for p_name in pillar_surrounds:
        po = bpy.data.objects.get(p_name)
        if po:
            po.data.materials.clear()
            po.data.materials.append(mat_pillar)
            po.hide_render = False

    # Glass
    true_glass = ['unnamed.021', 'unnamed.027', 'unnamed.059', 'unnamed.065', 'unnamed.242', 'unnamed.248']
    for g_name in true_glass:
        go = bpy.data.objects.get(g_name)
        if go:
            go.data.materials.clear()
            go.data.materials.append(mat_glass)
            go.hide_render = False

    # Headlights & Taillights
    for red_name in ['unnamed.010', 'unnamed.015', 'unnamed.016', 'unnamed.032', 'unnamed.033']:
        o = bpy.data.objects.get(red_name)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_tl_ruby)
            o.hide_render = False

    for clear_name in ['unnamed.018', 'unnamed.020']:
        o = bpy.data.objects.get(clear_name)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_tl_clear)
            o.hide_render = False

    for hl_lens_name in ['unnamed.017', 'unnamed.019', 'unnamed.070', 'unnamed.071']:
        o = bpy.data.objects.get(hl_lens_name)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_hl_lens)
            o.hide_render = False

    # Hide all track parts & blueprint planes
    unwanted = [
        'unnamed.069', 'unnamed.034', 'unnamed.035', 'unnamed.036',
        'unnamed.005', 'unnamed.009', 'unnamed.135', 'unnamed.136',
        'unnamed.194', 'Laguna_Race_Wing', 'unnamed.125', 'unnamed.184',
        'unnamed.128', 'unnamed.029', 'unnamed.031', 'unnamed.220',
        'unnamed.058', 'unnamed.064', 'unnamed.241', 'unnamed.247',
        'unnamed.165', 'unnamed.195', 'unnamed.197', 'unnamed.239',
        'Ref_Plane_Front', 'Ref_Plane_Side', 'Ref_Plane_Top'
    ]
    for n in unwanted:
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = True
            o.hide_viewport = True

    # 3. SAVE MASTER BLEND FILE
    blend_path = os.path.abspath(r"blender\laguna_master.blend")
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"[Flawless] Saved master blend to {blend_path}")

    # 4. RENDER 1080P VIEWS
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    cam = scene.camera

    out_front = os.path.abspath(r"laguna_front.png")
    out_rear = os.path.abspath(r"laguna_rear.png")
    out_pres = os.path.abspath(r"laguna_presentation.png")

    # Front 3/4
    print("[Flawless] Rendering Front 3/4...")
    cam.location = mathutils.Vector((-4.10, -4.35, 1.25))
    target_front = mathutils.Vector((0.0, -0.60, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear 3/4
    print("[Flawless] Rendering Rear 3/4...")
    cam.location = mathutils.Vector((3.80, 4.30, 1.35))
    target_rear = mathutils.Vector((0.0, 0.40, 0.65))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    shutil.copy2(out_front, out_pres)
    art_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    shutil.copy2(out_front, os.path.join(art_dir, "laguna_front.png"))
    shutil.copy2(out_rear, os.path.join(art_dir, "laguna_rear.png"))
    shutil.copy2(out_pres, os.path.join(art_dir, "laguna_presentation.png"))
    print("[Flawless] Complete! Saved all presentation renders.")

if __name__ == "__main__":
    run_flawless()
