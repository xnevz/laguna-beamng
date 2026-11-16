"""
Final polish:
1. Re-position Moulding_Rear_Bumper to Z=0.55-0.58 so it runs across the bumper and cleanly incorporates the sensor/tow cap area, matching ref_rear.jpg.
2. Hide unnamed.058, 064, 241, 247 (inner door cards) so Solarglass windows are clear and let light through.
3. Assign unnamed.149 and 150 to Laguna_Interior_Charcoal so no silver bars show through the rear window.
4. Remove trunk pins from unnamed.025.
5. Render final 1080p images.
"""

import bpy
import bmesh
import mathutils
import math
import os
import shutil

def run_polish():
    print("Applying final polish...")

    mat_body = bpy.data.materials.get("Laguna_Champagne_Silver")
    mat_trim = bpy.data.materials.get("Laguna_Trim_Charcoal")
    mat_interior = bpy.data.materials.get("Laguna_Interior_Charcoal")

    # 1. Hide inner door cards that blocked glass transparency
    for n in ['unnamed.058', 'unnamed.064', 'unnamed.241', 'unnamed.247']:
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = True
            o.hide_viewport = True

    # 2. Make internal struts inside rear window dark interior charcoal
    for n in ['unnamed.149', 'unnamed.150', 'unnamed.213', 'unnamed.214', 'unnamed.030', 'unnamed.155']:
        o = bpy.data.objects.get(n)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_interior)

    # 3. Remove trunk pins from unnamed.025
    o25 = bpy.data.objects.get('unnamed.025')
    if o25:
        bm = bmesh.new()
        bm.from_mesh(o25.data)
        # Pins are small loose loops on top of the decklid at Z > 0.92
        to_del = [f for f in bm.faces if all(v.co.z > 0.93 for v in f.verts) and len(f.verts) == 3]
        if to_del:
            bmesh.ops.delete(bm, geom=to_del, context='FACES')
            bm.to_mesh(o25.data)
            o25.data.update()
            print(f"Removed {len(to_del)} pin faces from unnamed.025")
        bm.free()

    # 4. Remove standalone Rear_Bumper_Plug and integrate continuous Rear Bumper Rub Strip
    old_plug = bpy.data.objects.get("Rear_Bumper_Plug")
    if old_plug:
        bpy.data.objects.remove(old_plug, do_unlink=True)

    old_rbm = bpy.data.objects.get("Moulding_Rear_Bumper")
    if old_rbm:
        bpy.data.objects.remove(old_rbm, do_unlink=True)

    mesh_rbm = bpy.data.meshes.new("Moulding_Rear_Bumper_Mesh")
    obj_rbm = bpy.data.objects.new("Moulding_Rear_Bumper", mesh_rbm)
    bpy.context.collection.objects.link(obj_rbm)

    # Clean curved wrap-around bumper rub strip running at Z=0.55-0.60
    # Following the exact curvature of the Laguna II rear bumper
    pts = [
        (-0.83, 1.82, 0.56),
        (-0.84, 1.95, 0.57),
        (-0.80, 2.08, 0.58),
        (-0.66, 2.15, 0.59),
        (-0.40, 2.19, 0.60),
        ( 0.00, 2.21, 0.60),
        ( 0.40, 2.19, 0.60),
        ( 0.66, 2.15, 0.59),
        ( 0.80, 2.08, 0.58),
        ( 0.84, 1.95, 0.57),
        ( 0.83, 1.82, 0.56)
    ]
    h = 0.026 # 52mm strip height
    thick = 0.008
    rb_verts = []
    rb_faces = []
    for i, pt in enumerate(pts):
        # Base vertex against bumper
        rb_verts.append(mathutils.Vector((pt[0], pt[1], pt[2] - h)))
        rb_verts.append(mathutils.Vector((pt[0], pt[1], pt[2] + h)))
        # Outer protruding vertex
        nx = 0.0 if abs(pt[0]) < 0.1 else (pt[0] / abs(pt[0])) * 0.4
        ny = 0.9
        rb_verts.append(mathutils.Vector((pt[0] + nx * thick, pt[1] + ny * thick, pt[2] - h + 0.004)))
        rb_verts.append(mathutils.Vector((pt[0] + nx * thick, pt[1] + ny * thick, pt[2] + h - 0.004)))

    for i in range(len(pts) - 1):
        idx1 = i * 4
        idx2 = (i + 1) * 4
        # Outer face
        rb_faces.append((idx1 + 2, idx2 + 2, idx2 + 3, idx1 + 3))
        # Top bevel
        rb_faces.append((idx1 + 1, idx2 + 1, idx2 + 3, idx1 + 3))
        # Bottom bevel
        rb_faces.append((idx1 + 0, idx2 + 0, idx2 + 2, idx1 + 2))

    mesh_rbm.from_pydata(rb_verts, [], rb_faces)
    mesh_rbm.update()
    obj_rbm.data.materials.append(mat_trim)

    # 5. Flush backing patch behind the rub strip at the hole location
    mesh_patch = bpy.data.meshes.new("Bumper_Hole_Patch_Mesh")
    obj_patch = bpy.data.objects.new("Bumper_Hole_Patch", mesh_patch)
    bpy.context.collection.objects.link(obj_patch)
    p_pts = [
        mathutils.Vector((0.56, 2.06, 0.51)),
        mathutils.Vector((0.74, 2.06, 0.51)),
        mathutils.Vector((0.74, 2.14, 0.64)),
        mathutils.Vector((0.56, 2.14, 0.64))
    ]
    mesh_patch.from_pydata(p_pts, [], [(0, 1, 2, 3)])
    mesh_patch.update()
    obj_patch.data.materials.append(mat_trim)

    # 6. Render high-res 1080p images
    scene = bpy.context.scene
    cam = scene.camera
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    out_front = os.path.abspath(r"laguna_front.png")
    out_rear = os.path.abspath(r"laguna_rear.png")
    out_pres = os.path.abspath(r"laguna_presentation.png")

    # Front 3/4
    print("[Render] Rendering Front 3/4...")
    cam.location = mathutils.Vector((-4.10, -4.35, 1.25))
    target_front = mathutils.Vector((0.0, -0.60, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear 3/4
    print("[Render] Rendering Rear 3/4...")
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
    print("[Polish] Successfully rendered and saved!")

if __name__ == "__main__":
    run_polish()
