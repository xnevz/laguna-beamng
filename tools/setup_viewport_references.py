"""
Texture reference planes in Blender with the downloaded Laguna images.
"""

import bpy
import os

def setup_reference_textures():
    ref_dir = os.path.abspath(r"blender\references")
    side_img_path = os.path.join(ref_dir, "laguna2_side.jpg")
    front_img_path = os.path.join(ref_dir, "laguna2_front.jpg")

    def create_image_material(mat_name, img_path):
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        node_tex = nodes.new(type='ShaderNodeTexImage')
        if os.path.exists(img_path):
            node_tex.image = bpy.data.images.load(img_path, check_existing=True)

        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        node_bsdf.inputs['Roughness'].default_value = 1.0
        node_bsdf.inputs['Specular IOR Level'].default_value = 0.0

        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
        links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
        return mat

    # Side Plane
    side_plane = bpy.data.objects.get("Ref_Plane_Side")
    if side_plane and os.path.exists(side_img_path):
        mat_side = create_image_material("Mat_Ref_Side", side_img_path)
        if not side_plane.data.materials:
            side_plane.data.materials.append(mat_side)
        else:
            side_plane.data.materials[0] = mat_side
        print("[References] Textured Ref_Plane_Side with laguna2_side.jpg")

    # Front Plane
    ref_col = bpy.data.collections.get("00_References_Blueprints")
    if not ref_col:
        ref_col = bpy.context.scene.collection

    front_plane = bpy.data.objects.get("Ref_Plane_Front")
    if not front_plane:
        bpy.ops.mesh.primitive_plane_add(
            size=1.0,
            location=(0.0, 2.45, 1.43 / 2.0),
            rotation=(1.570796, 0.0, 0.0)
        )
        front_plane = bpy.context.active_object
        front_plane.name = "Ref_Plane_Front"
        front_plane.scale = (1.75, 1.43, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        for col in front_plane.users_collection:
            col.objects.unlink(front_plane)
        ref_col.objects.link(front_plane)

    if os.path.exists(front_img_path):
        mat_front = create_image_material("Mat_Ref_Front", front_img_path)
        if not front_plane.data.materials:
            front_plane.data.materials.append(mat_front)
        else:
            front_plane.data.materials[0] = mat_front
        print("[References] Textured Ref_Plane_Front with laguna2_front.jpg")

if __name__ == "__main__":
    setup_reference_textures()
