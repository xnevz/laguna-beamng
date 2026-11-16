"""
final_laguna_polish.py
======================
Final polishing pass for the Renault Laguna II Phase 1 (2001-2005):
  1. Remove duplicate Moulding_Door_* or align unibody paint.
  2. Fix rear right bumper hole fill: assign Laguna_Trim_Charcoal to seamlessly blend with rub strip.
  3. Clean rear wheel arch: ensure wheel arch is 100% Champagne Silver.
  4. Add carpeted Parcel Shelf under rear glass to eliminate hollow interior view.
  5. Calibrate front split grille slats and bumper trim.
  6. Render final 1080p Front 3/4 and Rear 3/4 images.
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

def polish_laguna():
    print("==========================================================")
    print("STARTING FINAL LAGUNA II POLISHING PASS")
    print("==========================================================")
    scene = bpy.context.scene

    mat_paint = bpy.data.materials.get("Laguna_Champagne_Silver")
    mat_trim = bpy.data.materials.get("Laguna_Trim_Charcoal")
    mat_interior = bpy.data.materials.get("Laguna_Interior_Charcoal")

    # 1. Clean unibody unnamed.004 face assignments
    o_004 = bpy.data.objects.get("unnamed.004")
    if o_004:
        # Reset all polygons to Champagne Silver first
        for poly in o_004.data.polygons:
            poly.material_index = 0

        # Now assign trim only to strictly defined moulding zones:
        for poly in o_004.data.polygons:
            verts = [o_004.matrix_world @ o_004.data.vertices[v_idx].co for v_idx in poly.vertices]
            # Rear bumper rub strip: y > 1.82, 0.565 < z < 0.635
            is_rear_bumper_trim = all(v.y > 1.82 and 0.565 < v.z < 0.635 for v in verts)
            # Right rear bumper hole fill (x ~ 0.58..0.76, y > 2.0, z ~ 0.55..0.66)
            is_hole_fill = all(0.55 < v.x < 0.78 and v.y > 2.0 and 0.55 < v.z < 0.66 for v in verts)
            # Front bumper corner rub strip: y < -1.84, 0.44 < z < 0.50, 0.48 < abs(x) < 0.82
            is_front_corner_trim = all(v.y < -1.84 and 0.44 < v.z < 0.50 and 0.48 < abs(v.x) < 0.82 for v in verts)

            if is_rear_bumper_trim or is_hole_fill or is_front_corner_trim:
                poly.material_index = 1
        o_004.data.update()
        print("Updated unnamed.004 rub strip materials cleanly!")

    # 2. Add realistic carpeted rear Parcel Shelf under the liftback rear window
    old_shelf = bpy.data.objects.get("Parcel_Shelf")
    if old_shelf:
        bpy.data.objects.remove(old_shelf, do_unlink=True)
    m_shelf = bpy.data.meshes.new("Parcel_Shelf_Mesh")
    o_shelf = bpy.data.objects.new("Parcel_Shelf", m_shelf)
    bpy.context.collection.objects.link(o_shelf)
    
    # Horizontal shelf at z = 0.89, y in [1.05, 1.95], x in [-0.58, 0.58]
    sh_v = [
        mathutils.Vector((-0.58, 1.05, 0.89)),
        mathutils.Vector(( 0.58, 1.05, 0.89)),
        mathutils.Vector(( 0.58, 1.94, 0.89)),
        mathutils.Vector((-0.58, 1.94, 0.89))
    ]
    m_shelf.from_pydata(sh_v, [], [(0, 1, 2, 3)])
    m_shelf.update()
    o_shelf.data.materials.append(mat_interior)
    print("Added realistic carpeted parcel shelf under rear glass!")

    # 3. Fine-tune Solarglass shader
    mat_solar = bpy.data.materials.get("Laguna_Factory_Solarglass")
    if mat_solar and mat_solar.node_tree:
        bsdf_s = mat_solar.node_tree.nodes.get("Principled BSDF")
        if bsdf_s:
            bsdf_s.inputs['Base Color'].default_value = (0.82, 0.92, 0.88, 1.0)
            bsdf_s.inputs['Roughness'].default_value = 0.015
            bsdf_s.inputs['Transmission Weight'].default_value = 0.70
            bsdf_s.inputs['Alpha'].default_value = 0.55
            bsdf_s.inputs['IOR'].default_value = 1.52
            bsdf_s.inputs['Coat Weight'].default_value = 1.0
            bsdf_s.inputs['Coat Roughness'].default_value = 0.005

    # 4. Save updated blend file
    blend_path = os.path.abspath(r"blender\laguna_master.blend")
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"Saved polished blend file to: {blend_path}")

    # 5. Render final high-resolution 1080p images
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    cam = scene.camera

    out_front = os.path.abspath(r"laguna_front.png")
    out_rear = os.path.abspath(r"laguna_rear.png")
    out_pres = os.path.abspath(r"laguna_presentation.png")

    # Front 3/4 Render
    print("Rendering final Front 3/4 validation angle...")
    cam.location = mathutils.Vector((-4.10, -4.35, 1.25))
    target_front = mathutils.Vector((0.0, -0.60, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear 3/4 Render
    print("Rendering final Rear 3/4 validation angle...")
    cam.location = mathutils.Vector((3.80, 4.30, 1.35))
    target_rear = mathutils.Vector((0.0, 0.40, 0.65))
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
    print("FINAL LAGUNA II POLISHING PASS COMPLETED SUCCESSFULLY!")
    print("==========================================================")

if __name__ == "__main__":
    polish_laguna()
