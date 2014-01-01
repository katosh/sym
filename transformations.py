import globals as g
from mathutils import Vector
import math
import bpy

### PAIRING -> TRANSFORMATIONS ###

class transf:
    scal = 1                # scaling
    (rx,ry,rz) = (0,0,0)    # rotation arround this vector
    rr = 0                  # rotation angle
    (tx,ty,tz) = (0,0,0)    # translation vector
    rnor=Vector()           # reflection normal
    roff=Vector()           # reflection offset in normal direction
    p = None                # Vertex 1
    pc = 0                  # Curvature of Vertex 1
    q = None                # Vertex 2
    qc = 0                  # Curvature of Vertex 2

def mktransfs():
    for i,p in enumerate(g.sigs):
        k=i+1
        # pairing with the followers in the array sortet by curvatures
        while ((k < g.nsigs) and
                # only pair points of similar curvatures
                (abs( 1 - (g.sigs[k].curv / p.curv) )) < g.plimit and 
                # ... and if the verts have differen positions 
                (p.vert.co-g.sigs[k].vert.co).length != 0) :
            this = transf()
            this.p=p.vert
            this.q=g.sigs[k].vert
            
            (this.tx,this.ty,this.tz) = this.p.co - this.q.co  # translation
            (this.ry,this.ry,this.rz,this.rr) = \
                    this.p.normal.rotation_difference(this.q.normal) # rotation
            
            # normal calculation
            this.rnor = this.p.co-this.q.co 
            this.rnor.normalize()
            # offset calculation in the normal direction
            hypertenuse = (this.p.co + this.q.co) / 2
            if hypertenuse.length == 0:
                this.off = 0
            else:
                alpha           = min(hypertenuse.angle(this.rnor), 
                                         math.pi - hypertenuse.angle(this.rnor))
                this.roff       = math.cos(alpha) * hypertenuse.length
                g.moff          = max( this.roff , g.moff )
                if g.mioff is None:
                    g.mioff     = this.roff
                g.mioff         = min( this.roff , g.mioff )
            g.transfs.append(this)
            k+=1
    g.ntransfs = len(g.transfs)

## plotting transformation space for reflectation
def plotr():
    plot = []
    for t in g.transfs:
        p = Vector()
        if t.rnor.x == 0:
            p.y = math.pi/2
        else:
            p.y = math.atan(t.rnor.y/t.rnor.x)  # phi
        p.x = -math.acos(t.rnor.z)              # theta
        p.z = t.roff                            # offset
        plot.append(p)
    pmesh = bpy.data.meshes.new("Plot")
    pmesh.from_pydata(plot,[],[])
    ob_plot = bpy.data.objects.new("Plot", pmesh)     
    g.scene.objects.link(ob_plot)
