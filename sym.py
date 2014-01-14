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

    # using globals to save last calculated spaces for debugging
    global sigs, gamma, clusters, track

    scene=bpy.context.scene
    if obj == None:
        obj = bpy.context.object # take active object

    print('calculating signatures...')
    sigs = sign.Signatures(obj,**args)
    sign.plot(sigs=sigs, scene=scene)
    print('calculated',len(sigs),'signatures')

    print('filling the transformation space...')
    gamma = Gamma(sigs,group=transformations.Reflection)
    print('found',len(gamma),'transformations')
    gamma.plot(scene,label="transformations")


    print('clustering...')
    clusters, track = cluster(gamma)
    print('found',len(clusters),'clusters')
    clusters.plot(scene,label="clusters")
    track.plot(bpy.context.scene,label="track")

    show_reflection_planes(clusters=clusters,scene=scene)

    return sigs,gamma,clusters

def debug(profile=True, **args):
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

def debug(profile=True, mkobj=False, **args):
    """ reload modules, invoke profiler """
    if mkobj:
        args.update({'obj': createsuzanne()})
    if profile:
        import cProfile, pstats, io
        pr = cProfile.Profile()
        pr.enable()
        ret=run(**args)
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).strip_dirs()
        ps.sort_stats('cumulative')
        ps.print_stats(10)
        print(s.getvalue())
        return ret
    else:
        return run(**args)

def reload():
    """ reload modules """
    import imp, sym, signatures, transformations, meanshift, ui
    imp.reload(sym)
    imp.reload(signatures)
    imp.reload(transformations)
    imp.reload(meanshift)
    imp.reload(ui)

# autostart
if __name__ == "__main__": # when started from console, directly run
    debug() # dominiks framework
