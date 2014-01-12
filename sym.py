import sys
sys.path.append(r'.')   # add script path to system pathes to find the other modules
import bpy, bmesh

import signatures as sign
from transformations import Gamma
from meanshift import cluster
from verification import show_reflection_planes
import transformations

def run(obj=None, **args):
    """ runs symmetry detection on the obj
    active object is taken if none is given"""
    scene=bpy.context.scene
    if obj == None:
        obj = bpy.context.object # take active object

    print('calculating signatures...')
    sigs = sign.Signatures(obj,**args)
    sign.show(sigs=sigs, scene=scene)
    print('calculated',len(sigs),'signatures')

    print('filling the transformation space...')
    gamma = Gamma(sigs,group=transformations.Reflection)
    print('found',len(gamma),'transformations')
    gamma.plot(scene,label="transformations")


    print('clustering...')
    clusters = cluster(gamma)
    print('found',len(clusters),'clusters')
    clusters.plot(scene,label="clusters")

    show_reflection_planes(clusters=clusters,scene=scene)

    # using globals to save last calculated spaces for external use (selections)
    # todo: try to somehow append the spaces to the blender plot objects
    global lastclusters, lastgamma
    lastclusters=clusters
    lastgamma=gamma
    return sigs,gamma,clusters

def debug(profile=True,prune_perc=0.5, **args):
    """ reload modules, invoke profiler """
    rel()
    if profile:
        import cProfile, pstats, io
        pr = cProfile.Profile()
        pr.enable()
        run(prune_perc=prune_perc, **args)
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).strip_dirs()
        ps.sort_stats('cumulative')
        ps.print_stats(10)
        print(s.getvalue())

def createsuzanne():
    import bmesh
    bm=bmesh.new()
    bpy.ops.object.delete()            # deleting the stupid cube
    bpy.ops.mesh.primitive_monkey_add()
    bpy.ops.object.delete()
    bm.from_mesh(bpy.data.meshes["Suzanne"]) # get mesh data from model
    mesh = bpy.data.meshes.new("Suzanne")
    bm.to_mesh(mesh)
    ob_new = bpy.data.objects.new("Suzanne", mesh)
    ob_new.hide = True
    bpy.context.scene.objects.link(ob_new)
    return ob_new
    
def test(p=False, tobj=None, mkobj=False):
    import imp, cProfile, sym, signatures, transformations, meanshift
    rel()
    if p and mkobj:
        cProfile.run('run(createsuzanne())')
    elif p:
        cProfile.run('run()')
    else:
        return run(**args)

def rel():
    """ reload modules """
    import imp, sym, signatures, transformations, meanshift
    imp.reload(sym)
    imp.reload(signatures)
    imp.reload(transformations)
    imp.reload(meanshift)

### Methods for selection, maybe put into own module

def sel_selected_cluster(clusters=None):
    """ take selected clusters and select according transformations """
    if clusters==None:
        global lastclusters
        clusters = lastclusters
    for cluster_index in get_sel_vert(clusters.obj):
        sel_transformations(clusters[cluster_index].clusterverts)

def sel_transformations(transformations):
    bm = get_bmesh(transformations[0].gamma.obj)
    sel_verts(transformations[0].gamma.obj, [t.index for t in transformations])

def sel_verts(obj, vert_indices, select=True):
    """ selects the given vertices from the Object via their index"""
    bm = get_bmesh(obj, edit=True)
    for i in vert_indices:
        bm.verts[i].select = select

def get_sel_vert(obj):
    """ returns indices of selected vertices """
    bm = get_bmesh(obj)
    return [vert.index for vert in bm.verts if vert.select]

def get_bmesh(obj,edit=False):
    """ returns the BMesh to the object, writeable if edit is True """
    if edit:
        bpy.context.scene.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
    if obj.mode=='EDIT':
        return bmesh.from_edit_mesh(obj.data)
    elif obj.mode=='OBJECT':
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        return bm

if __name__ == "__main__":
    test(p=True, mkobj=False)
