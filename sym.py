import sys
sys.path.append(r'.')   # add script path to system pathes to find the other modules
import bpy, bmesh

from signatures import Signatures
from meanshift import cluster
from verification import show_reflection_planes

import transformations

lastclusters = None
lastgamma = None

if __name__ == "__main__": # when started from console, directly run
    debug()

def run(obj=None, **args):
    """ runs symmetry detection on the obj
    active object is taken if none is given"""
    scene=bpy.context.scene
    if obj == None:
        obj = bpy.context.object # take active object

    print('calculating signatures...')
    sigs = Signatures(obj,**args)
    print('calculated',len(sigs),'signatures')

    print('filling the transformation space...')
    gamma = transformations.Gamma(sigs,group=transformations.Reflection)
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
    else:
        return run(**args)

def rel():
    """ reload modules """
    import imp, sym, signatures, transformations, meanshift
    imp.reload(sym)
    imp.reload(signatures)
    imp.reload(transformations)
    imp.reload(meanshift)
