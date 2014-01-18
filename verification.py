import math
import bpy
from mathutils import Vector
from operator import attrgetter, itemgetter

### VERIFICATION ###

def show_reflection_planes(clusters=None, scene=bpy.context.scene, matrix_world=None):
    if len(clusters)==0: return
    print('the cluster densities are...')
    clusters.sort(key=lambda x: x.weight, reverse=True)
    maxdens = clusters[0].weight
    for cl in clusters:
        print(cl.weight,'at',cl.co)
        cl.draw(scene, maxdensity=maxdens, matrix_world=matrix_world)

def tfs_to_patch(tfs):
    tfs.sort(key=attrgetter('weight'), reverse=True)
    allocated = set()
    for tf in tfs:
        if not {tf.p, tf.q} & allocated: # empty intersection
            ppatch, qpatch = grow_patch(tf, allocated)
            allocated |= ppatch | qpatch # add sets
    return allocated

def get_patches(clusters):
    symmetries = []
    for c in clusters:
        clustertfs = c.clusterverts
        clustertfs.sort(key=attrgetter('weight'), reverse=True)
        allocated = set()
        for tf in clustertfs:
            if not {tf.p, tf.q} & allocated: # empty intersection
                ppatch, qpatch = grow_patch(tf, allocated)
                allocated |= ppatch | qpatch # add sets
                symmetries.append ( (c,tf,ppatch,qpatch) )
    return symmetries

def grow_patch(tf: "Transformation", allocated=set()) -> "(set(BMVert),set(BMVert))":
    # assuming tf.p/q are signatures

    ppatch = set( [tf.p] )
    qpatch = set( [tf.q] )

    queue = set()
    queue.add ( (tf.p,tf.q) )

    while len(queue)>0:
        p,q = queue.pop()
        neigh_p = get_neighbours(p) - ppatch - allocated
        neigh_q = get_neighbours(q) - qpatch - allocated

        for np in neigh_p:
            tnp = tf.apply(np.co)
            candidates=[]
            for nq in neigh_q:
                dist = (tnp-nq.co).length
                if dist < 0.01:
                    candidates.append((nq,dist))
            if candidates:
                candidates.sort(key=itemgetter(1), reverse=False) # sort by dist
                matchedq = candidates[0][0]
                queue.add( (np, matchedq) )
                ppatch.add( np )
                qpatch.add( matchedq )

    return (ppatch, qpatch)

def get_neighbours(sig):
    space = sig.space
    bmvert = space.get_bmvert(sig)
    return set(space.get_elem(e.other_vert(bmvert)) for e in bmvert.link_edges)
