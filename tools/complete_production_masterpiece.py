"""
Complete Production Masterpiece - Renault Laguna II Phase 1 (2001-2005)
1. Restores pristine trunk lid from blend1 and removes only race wing (Z > 1.02)
2. Turns ALL interior objects and Laguna_Metallic_Blue to authentic dark charcoal cockpit
3. Flattens the circular bumper recess in unnamed.004 so the rear bumper is 100% smooth
4. Solarglass: authentic pale green Solarglass with natural transparency into dark cabin
5. Natural daylight Nishita sky with soft warm sun and balanced exposure
6. Saves laguna_master.blend and renders 1080p Front 3/4 and Rear 3/4
"""

import bpy
import bmesh
import mathutils
import math
import os
import shutil

def run():
    print("==================================================")
    print("[Masterpiece] Executing Final Polish...")
    print("==================================================")
    scene = bpy.context.scene

    # 1. TURN ALL BLUE OBJECTS & SHADERS TO DARK INTERIOR CHARCOAL
    mat_interior = bpy.data.materials.get("Laguna_Interior_Charcoal")
    if not mat_interior:
        mat_interior = bpy.data.materials.new("Laguna_Interior_Charcoal")
        mat_interior.use_nodes = True
    in_bsdf = mat_interior.node_tree.nodes.get("Principled BSDF")
    if in_bsdf:
        in_bsdf.inputs['Base Color'].default_value = (0.035, 0.035, 0.04, 1.0)
        in_bsdf.inputs['Metallic'].default_value = 0.0
        in_bsdf.inputs['Roughness'].default_value = 0.85

    # Also neutralize Laguna_Metallic_Blue in case any object references it
    mat_blue = bpy.data.materials.get("Laguna_Metallic_Blue")
    if mat_blue and mat_blue.node_tree:
        b_bsdf = mat_blue.node_tree.nodes.get("Principled BSDF")
        if b_bsdf:
            b_bsdf.inputs['Base Color'].default_value = (0.035, 0.035, 0.04, 1.0)
            b_bsdf.inputs['Metallic'].default_value = 0.0
            b_bsdf.inputs['Roughness'].default_value = 0.85

    # Reassign all objects that had blue material to interior charcoal
    for o in bpy.data.objects:
        if o.type == 'MESH':
            for s in o.material_slots:
                if s.material and ('Blue' in s.material.name):
                    s.material = mat_interior

    # 2. RESTORE PRISTINE TRUNK LID FROM BLEND1
    old_o25 = bpy.data.objects.get("unnamed.025")
    blend1_path = os.path.abspath(r"blender\laguna_master.blend1")
    if os.path.exists(blend1_path):
        with bpy.data.libraries.load(blend1_path) as (data_from, data_to):
            if "unnamed.025" in data_from.objects:
                data_to.objects = ["unnamed.025"]
        
        imported_o25 = [o for o in data_to.objects if o is not None]
        if imported_o25:
            new_o25 = imported_o25[0]
            if old_o25:
                bpy.data.objects.remove(old_o25, do_unlink=True)
            new_o25.name = "unnamed.025"
            bpy.context.collection.objects.link(new_o25)
            
            # Remove only the race wing (faces at Z > 1.02)
            bm = bmesh.new()
            bm.from_mesh(new_o25.data)
            wing_faces = [f for f in bm.faces if min(v.co.z for v in f.verts) > 1.02]
            if wing_faces:
                bmesh.ops.delete(bm, geom=wing_faces, context='FACES')
                bm.to_mesh(new_o25.data)
                new_o25.data.update()
                print(f"[Masterpiece] Removed {len(wing_faces)} wing faces from restored trunk lid!")
            bm.free()
            
            mat_body = bpy.data.materials.get("Laguna_Champagne_Silver")
            new_o25.data.materials.clear()
            new_o25.data.materials.append(mat_body)
            new_o25.hide_render = False

    # 3. SMOOTH THE CIRCULAR BUMPER RECESS IN UNNAMED.004
    o4 = bpy.data.objects.get("unnamed.004")
    if o4:
        bm = bmesh.new()
        bm.from_mesh(o4.data)
        # Pull back/flatten any vertices inside the recess pocket (X in [0.55, 0.75], Y in [2.00, 2.15], Z in [0.50, 0.65])
        recess_verts = [v for v in bm.verts if 0.55 < v.co.x < 0.74 and 2.01 < v.co.y < 2.13 and 0.51 < v.co.z < 0.64]
        for v in recess_verts:
            # Flatten to outer surface curve (Y ~ 2.155)
            v.co.y = 2.155 - 0.05 * (v.co.x - 0.65)**2
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(o4.data)
        o4.data.update()
        bm.free()
        print(f"[Masterpiece] Smoothed {len(recess_verts)} vertices of bumper recess!")

    # 4. SOLARGLASS REFINEMENT
    mat_glass = bpy.data.materials.get("Laguna_Factory_Solarglass")
    if mat_glass and mat_glass.node_tree:
        g_bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
        if g_bsdf:
            g_bsdf.inputs['Base Color'].default_value = (0.84, 0.94, 0.89, 1.0) # Factory Renault Solarglass
            g_bsdf.inputs['Roughness'].default_value = 0.008
            g_bsdf.inputs['Alpha'].default_value = 0.28
            g_bsdf.inputs['IOR'].default_value = 1.52
            g_bsdf.inputs['Coat Weight'].default_value = 1.0
            g_bsdf.inputs['Coat Roughness'].default_value = 0.01

    # Window B-pillars & door surrounds -> Satin Black
    mat_pillar = bpy.data.materials.get("Laguna_Pillar_Black")
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

    # 5. NATURAL SUN & SKY
    world = scene.world
    nt = world.node_tree
    node_bg = nt.nodes.get("ShaderNodeBackground") or nt.nodes.get("Background")
    node_sky = nt.nodes.get("ShaderNodeTexSky")
    if node_sky:
        node_sky.sky_type = 'MULTIPLE_SCATTERING'
        node_sky.sun_elevation = math.radians(42.0)
        node_sky.sun_rotation = math.radians(-35.0)
        node_sky.altitude = 40.0
        node_sky.air_density = 1.0
        if hasattr(node_sky, 'aerosol_density'):
            node_sky.aerosol_density = 0.35
        node_sky.ozone_density = 1.8
        node_sky.sun_disc = True
        node_sky.ground_albedo = 0.15

    if node_bg:
        node_bg.inputs['Strength'].default_value = 0.65

    scene.view_settings.view_transform = 'AgX'
    try:
        scene.view_settings.look = 'AgX - High Contrast'
    except Exception:
        pass
    scene.view_settings.exposure = -2.60

    # 6. SAVE MASTER BLEND FILE
    blend_path = os.path.abspath(r"blender\laguna_master.blend")
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"[Masterpiece] Saved updated blend file to: {blend_path}")

    # 7. RENDER 1080P VIEWS
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    cam = scene.camera

    out_front = os.path.abspath(r"laguna_front.png")
    out_rear = os.path.abspath(r"laguna_rear.png")
    out_pres = os.path.abspath(r"laguna_presentation.png")

    # Front 3/4
    print("[Masterpiece] Rendering Front 3/4...")
    cam.location = mathutils.Vector((-4.10, -4.35, 1.25))
    target_front = mathutils.Vector((0.0, -0.60, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear 3/4
    print("[Masterpiece] Rendering Rear 3/4...")
    cam.location = mathutils.Vector((3.80, 4.30, 1.35))
    target_rear = mathutils.Vector((0.0, 0.40, 0.65))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    # Copy to artifacts directory
    shutil.copy2(out_front, out_pres)
    art_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    shutil.copy2(out_front, os.path.join(art_dir, "laguna_front.png"))
    shutil.copy2(out_rear, os.path.join(art_dir, "laguna_rear.png"))
    shutil.copy2(out_pres, os.path.join(art_dir, "laguna_presentation.png"))
    print("[Masterpiece] Complete! Photorealistic presentation renders saved.")

if __name__ == "__main__":
    run()
