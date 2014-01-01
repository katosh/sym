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
    p=0                     # Vertex 1
    q=0                     # Vertex 2

def mktransfs():
    for i,p in enumerate(g.sigs):
        k=i+1
        while ((k < g.laenge) and  # pairing with the followers in the array sortet by curvatures
                (abs( 1 - (g.sigs[k].curv / p.curv) )) < g.plimit and # only pair similar curvatures
                (p.co-g.sigs[k].co).length != 0) :                       # ... and iv the verts have differen positions 
            this = transf()
            this.p=p
            this.q=g.sigs[k]
            
            (this.tx,this.ty,this.tz)           = p.co - this.q.co  # translation
            (this.ry,this.ry,this.rz,this.rr)   = p.normal.rotation_difference(this.q.normal) # rotation
            
            # normal calculation
            this.rnor=p.co-this.q.co 
            this.rnor.normalize()
            # offset calculation in the normal direction
            hypertenuse     = (p.co + this.q.co) / 2
            if hypertenuse.length == 0:
                this.off = 0
            else:
                alpha           = abs(hypertenuse.angle(this.rnor) - (math.pi/2))
                this.roff       = math.sin(alpha) * hypertenuse.length
                g.moff          = max( this.roff , g.moff )
                if g.mioff is None:
                    g.mioff     = this.roff
                g.mioff         = min( this.roff , g.mioff )
            
            g.transfs.append(this)
            k=k+1

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
        p.z = t.roff                            #offset
        plot.append(p)
    pmesh = bpy.data.meshes.new("Plot")
    pmesh.from_pydata(plot,[],[])
    ob_plot = bpy.data.objects.new("Plot", pmesh)     
    g.scene.objects.link(ob_plot)
