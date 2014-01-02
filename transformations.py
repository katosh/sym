import globals as g
from mathutils import Vector
import math
import bpy

### PAIRING -> TRANSFORMATIONS ###

class transf:
    """ a transformation between two points of the geometry """
    def __init__(self, point1=None, point2=None):
        self.p = point1
        self.q = point2
        self.scal = 1
        self.trans = self.p.co - self.q.co
        # safe diam globaly
        g.diam = max(g.diam, self.trans.length)
        # calculate rotation vector and angle
        (self.rx,self.ry,self.rz, self.rr) = \
                self.p.normal.rotation_difference(self.q.normal)
        # normal calculation
        self.rnor = self.trans
        self.rnor.normalize()
        # offset calculation in the normal direction
        hypertenuse = (self.p.co + self.q.co) / 2
        if hypertenuse.length == 0:
            self.off = 0
        else:
            alpha = min(hypertenuse.angle(self.rnor), 
                    math.pi - hypertenuse.angle(self.rnor))
            self.roff = math.cos(alpha) * hypertenuse.length
            g.moff = max( self.roff , g.moff )
            if g.mioff is None:
                g.mioff = self.roff
            g.mioff = min( self.roff , g.mioff )
        # principal curvatures TODO
        self.pc1 = None
        self.pc2 = None
        self.qc1 = None
        self.qc2 = None
# sphere coordinates for reflection normal:
    def rnor_phi(self):
        if self.rnor.x == 0:
            return math.pi/2
        else:
            return math.atan(self.rnor.y/self.rnor.x)  # phi
    def rnor_theta(self):
        return math.acos(self.rnor.z)              # theta

def mktransfs():
    for i,p in enumerate(g.sigs):
        k=i+1
        # pairing with the followers in the array sortet by curvatures
        while ((k < g.nsigs) and
                # only pair points of similar curvatures
                (abs( 1 - (g.sigs[k].curv / p.curv) )) < g.plimit and 
                # ... and if the verts have differen positions 
                (p.vert.co-g.sigs[k].vert.co).length != 0) :
            this = transf(point1=p.vert, point2=g.sigs[k].vert)
            g.transfs.append(this)
            k+=1
    g.ntransfs = len(g.transfs)

## plotting transformation space for reflectation
def plotr():
    plot = []
    for t in g.transfs:
        p = Vector()
        p.x = t.rnor_phi()
        p.y = t.rnor_theta()
        p.z = t.roff                            # offset
        plot.append(p)
    pmesh = bpy.data.meshes.new("Plot")
    pmesh.from_pydata(plot,[],[])
    ob_plot = bpy.data.objects.new("Plot", pmesh)     
    g.scene.objects.link(ob_plot)
