import math
import bpy
from mathutils import Vector

### VERIFICATION ###

def showplane(plane):
    base = plane.rnor * plane.roff
    rme = bpy.data.meshes.new('rNormal')
    normalverts = [base, base + g.bref.rnor]
    normaledge = [[0, 1]]
    rme.from_pydata(normalverts,normaledge,[])
    ob_normal = bpy.data.objects.new("rNormal", rme)
    g.scene.objects.link(ob_normal)

    n = Vector() # plane rotation in (phi,theta,0)
    n.xyz = (plane.co.x,
        -plane.co.y,
        0)
    bpy.ops.mesh.primitive_plane_add(
            radius=5,
            location = base,
            rotation=n.zyx)

def show_reflection_planes(clusters=None, scene=bpy.context.scene):
    print('the cluster densities are...')
    for cl in clusters:
        print(cl.density,'at',cl.co)
        cl.draw(scene)

def get_patches(clustertfs=[]):
    #assume clusterverts are sorted by weight for reasonable results
    allocated = Set()
    for tf in clustertfs:
        if not {tf.p, tf.q} & allocated
            ppatch, qpatch = grow_patch(clustertfs[0])
            allocated = allocated | ppatch | qpatch # union of the sets


def grow_patch(tf: "Transformation") -> "(Set(BMVert),Set(BMVert))":
    # assuming tf.p/q are of type BMVert

    ppatch = Set( [tf.p] )
    qpatch = Set( [tf.q] )

    queue = Set( (tf.p,tf.q) )

    while len(queue)>0:
        p,q = queue.pop()
        neigh_p = get_neighbours(p) - ppatch
        neigh_q = get_neighbours(q) - qpatch

        for np in neigh_p:
            tnp = tf.apply(np)
            candidates=[]
            for nq in neigh_q:
                dist = (tnp.co-nq.co).length
                if dist < 0.01:
                    candidates.append((nq,dist))
            if candidates:
                candidates.sort(key=itemgetter(1), reverse=False) # sort by dist
                queue.add( (np,candidates[0]) )
                ppatch.add( np )
                qpatch.add( candidates[0] )

    return (ppatch, qpatch)

def get_neighbours(bmvert) -> "Set(BMVert)":
    return Set(e.other_vert(bmvert) for e in bmvert.link_edges)
