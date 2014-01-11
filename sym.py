import sys
sys.path.append(r'.')   # add script path to system pathes to find the other modules
import bpy, bmesh

from signatures import mksigs
from transformations import Gamma
from meanshift import cluster
from verification import show_reflection_planes

def run(obj=None):
    scene=bpy.context.scene
    bm=bmesh.new()
    
    if type(obj)==bpy.types.Object:
        bm.from_mesh(obj.data)
    else:
        bm.from_mesh(bpy.context.object.data)
    
    scene=bpy.context.scene
    
    print('calculating signatures...')
    sigs = mksigs(bm.verts)
    print('calculated',len(sigs),'signatures')

    print('filling the transformation space...')
    gamma = Gamma(sigs)
    print('found',len(gamma),'transformations')
    gamma.plot(scene,label="transformations")
    

    print('clustering...')
    clusters=cluster(gamma)
    print('found',len(clusters),'clusters')
    clusters.plot(scene,label="clusters")

    show_reflection_planes(clusters=clusters,scene=scene)

def createsuzanne():
    import bmesh
    bm=bmesh.new()
    bpy.ops.object.delete()            # deleting the stupid cube
    bpy.ops.mesh.primitive_monkey_add()
    bpy.ops.object.delete()
    bm.from_mesh(bpy.data.meshes["Suzanne"]) # get mesh data from model
    mesh = bpy.data.meshes.new("Apemesh")
    bm.to_mesh(mesh)
    ob_new = bpy.data.objects.new("Apeobj", mesh)
    ob_new.hide = True
    bpy.context.scene.objects.link(ob_new)
    return ob_new
    
def test(p=False, tobj=None, mkobj=False):
    import imp, cProfile, sym, signatures, transformations, meanshift
    imp.reload(imp)
    imp.reload(sym)
    imp.reload(signatures)
    imp.reload(transformations)
    imp.reload(meanshift)
        
    if p and mkobj:
        cProfile.run('run(createsuzanne())')
    elif p:
        cProfile.run('run()')
    else:
        sym.run(obj=tobj)

if __name__ == "__main__":
    test(p=True, mkobj=False)
