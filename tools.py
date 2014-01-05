import bpy

def plot_verts(name,vectors,scene=bpy.context.scene):
    """ plots vertices """
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vectors, [], [])
    obj = bpy.data.objects.new(name, mesh)
    scene.objects.link(obj)
	
def plot_plane(name,normal,offset):
	pass