"""
Separate the TCC rear race wing from the trunk lid, and hide the race wing.
"""

import bpy
import bmesh

def separate_race_wing():
    o = bpy.data.objects.get('unnamed.025')
    if not o:
        print("unnamed.025 not found!")
        return

    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o

    bm = bmesh.new()
    bm.from_mesh(o.data)

    # Find faces belonging to the wing (Z > 0.96 and Y between 1.95 and 2.15 on the raised wing blade and brackets)
    wing_faces = []
    trunk_faces = []

    # Let's inspect disconnected islands in bm
    visited = set()
    islands = []
    for f in bm.faces:
        if f in visited: continue
        island = []
        queue = [f]
        visited.add(f)
        while queue:
            curr = queue.pop(0)
            island.append(curr)
            for edge in curr.edges:
                for linked in edge.link_faces:
                    if linked not in visited:
                        visited.add(linked)
                        queue.append(linked)
        islands.append(island)

    # Islands 6, 7, 8, 9 are the race wing blade and struts
    wing_face_set = set()
    for i in [6, 7, 8, 9]:
        if i < len(islands):
            for f in islands[i]:
                wing_face_set.add(f)

    # If wing faces found, create a new object for the wing and delete from trunk
    if wing_face_set:
        bm_wing = bmesh.new()
        face_map = {}
        for f in wing_face_set:
            new_verts = []
            for v in f.verts:
                nv = bm_wing.verts.new(v.co)
                new_verts.append(nv)
            try:
                bm_wing.faces.new(new_verts)
            except:
                pass
        
        # Create wing object
        mesh_wing = bpy.data.meshes.new("Laguna_Race_Wing_Mesh")
        bm_wing.to_mesh(mesh_wing)
        bm_wing.free()
        
        obj_wing = bpy.data.objects.new("Laguna_Race_Wing", mesh_wing)
        bpy.context.collection.objects.link(obj_wing)
        obj_wing.matrix_world = o.matrix_world
        obj_wing.hide_render = True
        obj_wing.hide_viewport = True
        
        # Delete wing faces from trunk mesh
        bmesh.ops.delete(bm, geom=list(wing_face_set), context='FACES')
        bm.to_mesh(o.data)
        o.data.update()
        print(f"Successfully separated {len(wing_face_set)} wing faces into Laguna_Race_Wing and hid it!")
    else:
        print("No wing faces identified.")
        
    bm.free()

separate_race_wing()
