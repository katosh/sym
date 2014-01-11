import sys
sys.path.append(r'.')   # add script path to system pathes to find the other modules
import bpy, bmesh

from signatures import Signatures
from cluster import meanshift
from verification import show_reflection_planes

import transformations

lastclusters = None
lastgamma = None

def run(obj=bpy.context.object, **args):
    """ runs symmetry detection on the obj """

    print('calculating signatures...')
    sigs = Signatures(obj,**args)
    print('calculated',len(sigs),'signatures')

    print('filling the transformation space...')
    gamma = transformations.computeTransformations(sigs,group=transformations.Reflection)
    print('found',len(gamma),'transformations')
    gamma.plot(label="transformations")


    print('clustering...')
    clusters, traces = meanshift(gamma,**args)
    print('found',len(clusters),'clusters')
    clusters.plot(label="clusters")
    traces.plot(label="traces")

    show_reflection_planes(clusters)

    global lastclusters, lastgamma
    lastclusters=clusters
    lastgamma=gamma
    return sigs,gamma,clusters

def debug(profile=True,prune_perc=0.7, **args):
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
    import imp, sym, signatures, transformations, cluster
    imp.reload(sym)
    imp.reload(signatures)
    imp.reload(transformations)
    imp.reload(cluster)
    
#autostart
if __name__ == "main":
    debug()
else:
    debug(verbose=False)
