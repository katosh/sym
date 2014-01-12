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
    maxdens = 0
    for cl in clusters:
        print(cl.density,'at',cl.co)
        maxdens = max(maxdens, cl.density)
    for cl in clusters:
        cl.draw(scene, maxdensity=maxdens)
