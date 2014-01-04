""" Pairing and making of the Transformation-/Omega-Space """

import globals as g
from mathutils import Vector
import math
import bpy


class transf(object):
    """ a transformation between two points of the geometry """
    def __init__(self,
            point1=None,
            point2=None,
            signature1=None,
            signature2=None):
        if signature1:
            # principal curvatures TODO in signatures
            self.pc1 = signature1.pc1
            self.pc2 = signature1.pc2
            # total curvature
            self.pc = signature1.curv
            # point
            self.p = signature1.vert
        else:
            self.p = point1
            self.q = point2
        if signature2:
            self.qc1 = signature2.pc1
            self.qc2 = signature2.pc2
            # total curvature
            self.qc = signature2.curv
            # point
            self.q = signature2.vert
        else:
            self.q = point2
        self.scal = 1
        self.trans = self.p.co - self.q.co
        # safe diam globaly
        g.diam = max(g.diam, self.trans.length)
        # calculate rotation vector and angle
        (self.rx, self.ry, self.rz, self.rr) = \
                self.p.normal.rotation_difference(self.q.normal)
        # normal calculation
        self.rnor = self.trans
        self.rnor.normalize()
        # offset calculation in the normal direction
        hypotenuse = (self.p.co + self.q.co) / 2
        if hypotenuse.length == 0:
            self.off = 0
        else:
            alpha = min(hypotenuse.angle(self.rnor),
                    math.pi - hypotenuse.angle(self.rnor))
            self.roff = math.cos(alpha) * hypotenuse.length
            g.moff = max(self.roff, g.moff)
            if g.mioff is None:
                g.mioff = self.roff
            g.mioff = min(self.roff, g.mioff)
    # sphere coordinates for reflection normal:
    def rnor_phi(self):
        """ returnes phi of the spherical coordinates
        of the reflection normal """
        if self.rnor.x == 0:
            return math.pi/2
        else:
            return math.atan(self.rnor.y/self.rnor.x)
    def rnor_theta(self):
        """ returnes theta of the spherical coordinates
        of the reflection normal """
        return math.acos(self.rnor.z)

def mktransfs():
    """ fills the transformation space with all the transformation (pairing)"""
    for i in range(0,len(g.sigs)):
        k = i+1
        # pairing with the followers in the array sortet by curvatures
        while ((k < g.nsigs) and
                # only pair points of similar curvatures
                (abs(1 - (g.sigs[k].curv / g.sigs[i].curv))) < g.plimit and
                # ... and if the verts have differen positions
                (g.sigs[i].vert.co-g.sigs[k].vert.co).length != 0):
            this = transf(signature1=g.sigs[i], signature2=g.sigs[k])
            g.transfs.append(this)
            k += 1
    g.ntransfs = len(g.transfs)

def plotr():
    """ plotting transformation space for reflectation """
    plot = []
    for t in g.transfs:
        p = Vector()
        p.x = t.rnor_phi()
        p.y = t.rnor_theta()
        p.z = t.roff                            # offset
        plot.append(p)
    pmesh = bpy.data.meshes.new("Plot")
    pmesh.from_pydata(plot, [], [])
    ob_plot = bpy.data.objects.new("Plot", pmesh)
    g.scene.objects.link(ob_plot)
