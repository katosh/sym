import sys
sys.path.append(r'.')   # add script path to system pathes to find the other modules
import bpy, bmesh

scene=bpy.context.scene 
obj = bpy.context.object
bm = bmesh.new()
verts = obj.data.vertices
trans = obj.matrix_world

for v in verts:
    norm = v.normal*0.2
    edge = set()
    edge.add(bm.verts.new(trans*v.co))
    edge.add(bm.verts.new(trans*v.co + trans*norm))
    bm.edges.new(edge)


mesh = bpy.data.meshes.new("normals")
obj2  = bpy.data.objects.new("normals", mesh)
bm.to_mesh(mesh)
scene.objects.link(obj2)

