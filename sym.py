import sys
sys.path.append(r'.')   # add script path to system pathes to find the other modules
import bpy, bmesh

from signatures import mksigs
from transformations import Gamma
from meanshift import cluster

import transformations

if __name__ == "__main__": # when started from console, directly run
    run()

def run(obj=None):
    """ runs symmetry detection on the obj
    active object is taken if none is given"""
    scene=bpy.context.scene
    if obj == None:
        obj = bpy.context.object # take active object

    print('calculating signatures...')
    sigs = mksigs(obj.data.vertices)
    print('calculated',len(sigs),'signatures')

    print('filling the transformation space...')
    gamma = Gamma(sigs,group=transformations.Reflection)
    print('found',len(gamma),'transformations')
    gamma.plot(scene,label="transformations")


    print('clustering...')
    clusters = cluster(gamma)
    print('found',len(clusters),'clusters')
    clusters.plot(scene,label="clusters")

    # using globals to save last calculated spaces for external use (selections)
    # todo: try to somehow append the spaces to the blender plot objects
    global lastclusters, lastgamma
    lastclusters=clusters
    lastgamma=gamma

    return sigs,gamma,clusters

def debug(profile=True):
    """ reload modules, invoke profiler """
    import cProfile
    rel()
    if profile:
        cProfile.run('sym.run()')
    else:
        return run()

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