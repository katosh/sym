""" Pairing and making of the transformation space Gamma"""

from mathutils import Vector
import math
import bpy
import bmesh
import globals as g

class Transformations:
    """ representation of the transformation space also containing the blender object """
    
    transf_data=[] # passiert hier das gleiche wie mit self.transf_data=[] in __init__?
    
    def __init__(self):
        self.mesh = bpy.data.meshes.new("Transformations")
        self.obj  = bpy.data.objects.new("Transformations", self.mesh)
        self.bm   = bmesh.new()
    
    def add(self, t):
        self.transf_data.append(t)
        self.bm.verts.new(t.co)
    
    #todo: use bmesh edit mode for plotting
    def plot(self): 
        self.bm.to_mesh(self.mesh)
        g.scene.objects.link(self.obj)
        
        
        
    def __len__(self):
        return len(self.transf_data)

class Transf:
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
        # = projection of the midpoint in the normal direction
        self.roff = self.rnor * (self.p.co + self.q.co) / 2
        #compute coordinates in transformation space
        # (phi, theta, offset)
        self.co = Vector((math.atan(self.rnor.y/self.rnor.x) if self.rnor.x != 0 else math.pi/2,math.acos(self.rnor.z),self.roff))
        #compute min and max offsets
        g.moff = max(self.roff, g.moff)
        if g.mioff is None:
            g.mioff = self.roff
        g.mioff = min(self.roff, g.mioff)
        
        
def mktransfs():
    """ fills the transformation space with all the transformation (pairing)"""
    g.transfs = Transformations()
    for i in range(0,len(g.sigs)):
        k = i+1
        # pairing with the followers in the array sorted by curvatures
        while ((k < g.nsigs) and
                # only pair points of similar curvatures
                (abs(1 - (g.sigs[k].curv / g.sigs[i].curv))) < g.plimit and
                # ... and if the verts have different positions
                (g.sigs[i].vert.co-g.sigs[k].vert.co).length != 0):
            this = Transf(signature1=g.sigs[i], signature2=g.sigs[k])
            g.transfs.add(this)
            k += 1
    g.ntransfs = len(g.transfs)