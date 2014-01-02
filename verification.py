import globals as g
import math
import bpy
from mathutils import Vector

### VERIFICATION ###

def showplane():
    base = g.bref.rnor * g.bref.roff
    rme = bpy.data.meshes.new('rNormal')
    normalverts = [base, base + g.bref.rnor]
    normaledge = [[0, 1]]
    rme.from_pydata(normalverts,normaledge,[])
    ob_normal = bpy.data.objects.new("rNormal", rme)
    g.scene.objects.link(ob_normal)

    n = Vector() # plane rotation in (phi,theta,0)
    n.xyz = (g.bref.rnor_phi(),
        g.bref.rnor_theta(),
        0)
    bpy.ops.mesh.primitive_plane_add(radius=1.5, 
            location = base, 
            rotation=n.zyx)
