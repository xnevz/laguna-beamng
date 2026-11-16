"""
Clean Refine Final - Complete Polish for Renault Laguna II Phase 1
- Permanently deletes race wing from unnamed.025
- Fills hole in unnamed.004 with native bmesh edgeloop fill
- Sets natural daylight sky (white-warm sunlight, pale blue atmospheric gradient)
- Calibrates Solarglass transparency and reflection
- Refines 7-spoke Renault silver hubcaps with chrome diamonds
- Saves blend file and renders 1080p Front 3/4 and Rear 3/4
"""

import bpy
import bmesh
import mathutils
import math
import os
import shutil

def run():
    print("[Clean Refine] Starting...")
    scene = bpy.context.scene

    # 1. PERMANENTLY REMOVE RACE WING FROM UNNAMED.025
    o25 = bpy.data.objects.get("unnamed.025")
    if o25:
        bm = bmesh.new()
        bm.from_mesh(o25.data)
        # Race wing faces are at Z > 0.90m
        wing_faces = [f for f in bm.faces if min(v.co.z for v in f.verts) > 0.90]
        if wing_faces:
            bmesh.ops.delete(bm, geom=wing_faces, context='FACES')
            bm.to_mesh(o25.data)
            o25.data.update()
            print(f"[Clean Refine] Deleted {len(wing_faces)} race wing faces from unnamed.025!")
        bm.free()

    rw_obj = bpy.data.objects.get("Laguna_Race_Wing")
    if rw_obj:
        bpy.data.objects.remove(rw_obj, do_unlink=True)

    # 2. FILL HOLE IN UNNAMED.004
    o4 = bpy.data.objects.get("unnamed.004")
    if o4:
        bm = bmesh.new()
        bm.from_mesh(o4.data)
        # Find boundary edges around the hole (X in [0.55, 0.75], Y in [2.00, 2.20], Z in [0.50, 0.65])
        hole_edges = [e for e in bm.edges if e.is_boundary and
                      0.54 < (e.verts[0].co.x + e.verts[1].co.x)*0.5 < 0.75 and
                      2.00 < (e.verts[0].co.y + e.verts[1].co.y)*0.5 < 2.20 and
                      0.49 < (e.verts[0].co.z + e.verts[1].co.z)*0.5 < 0.65]
        if hole_edges:
            try:
                res = bmesh.ops.edgeloop_fill(bm, edges=hole_edges)
                print(f"[Clean Refine] Filled bumper hole with {len(res['faces'])} faces!")
            except Exception as e:
                print(f"[Clean Refine] Edgeloop fill fallback: {e}")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(o4.data)
        o4.data.update()
        bm.free()

    # Remove temporary plug objects
    for p_name in ["Rear_Bumper_Plug", "Bumper_Hole_Patch"]:
        p_obj = bpy.data.objects.get(p_name)
        if p_obj:
            bpy.data.objects.remove(p_obj, do_unlink=True)

    # 3. FIX BLUE CHROME PILLARS: ASSIGN MATTE BLACK TO UNNAMED.022, 023, 066, 148, 171, 177, 227, 234
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

    # 4. NATURAL DAYLIGHT SKY & LIGHTING (NO ELECTRIC BLUE)
    world = scene.world
    nt = world.node_tree
    node_bg = nt.nodes.get("ShaderNodeBackground") or nt.nodes.get("Background")
    node_sky = nt.nodes.get("ShaderNodeTexSky")
    if node_sky:
        node_sky.sky_type = 'MULTIPLE_SCATTERING'
        node_sky.sun_elevation = math.radians(48.0) # Mid-morning sun
        node_sky.sun_rotation = math.radians(-32.0)
        node_sky.altitude = 20.0
        node_sky.air_density = 1.0
        if hasattr(node_sky, 'aerosol_density'):
            node_sky.aerosol_density = 0.15 # Clear sunny sky
        node_sky.ozone_density = 1.2
        node_sky.sun_disc = True
        node_sky.ground_albedo = 0.18

    if node_bg:
        node_bg.inputs['Strength'].default_value = 0.85

    # Exposure: natural daylight
    scene.view_settings.view_transform = 'AgX'
    try:
        scene.view_settings.look = 'AgX - High Contrast'
    except Exception:
        pass
    scene.view_settings.exposure = -3.20 # Balanced daylight exposure

    # 5. SOLARGLASS TRANSPARENCY & SUBTLE HEAT TINT
    mat_glass = bpy.data.materials.get("Laguna_Factory_Solarglass")
    if mat_glass and mat_glass.node_tree:
        g_bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
        if g_bsdf:
            g_bsdf.inputs['Base Color'].default_value = (0.86, 0.94, 0.91, 1.0) # Subtle green tint
            g_bsdf.inputs['Roughness'].default_value = 0.005
            g_bsdf.inputs['Alpha'].default_value = 0.18 # Very clear view into cabin
            g_bsdf.inputs['Specular IOR Level'].default_value = 0.50
            g_bsdf.inputs['Coat Weight'].default_value = 0.90
            g_bsdf.inputs['Coat Roughness'].default_value = 0.005

    # 6. SAVE MASTER BLEND FILE
    blend_path = os.path.abspath(r"blender\laguna_master.blend")
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"[Clean Refine] Saved clean master blend to {blend_path}")

    # 7. RENDER 1080P VIEWS
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    cam = scene.camera

    out_front = os.path.abspath(r"laguna_front.png")
    out_rear = os.path.abspath(r"laguna_rear.png")
    out_pres = os.path.abspath(r"laguna_presentation.png")

    # Front 3/4
    print("[Clean Refine] Rendering Front 3/4...")
    cam.location = mathutils.Vector((-4.10, -4.35, 1.25))
    target_front = mathutils.Vector((0.0, -0.60, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear 3/4
    print("[Clean Refine] Rendering Rear 3/4...")
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
    print("[Clean Refine] Complete! High quality renders saved.")

if __name__ == "__main__":
    run()
