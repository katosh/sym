""" Pairing and making of the transformation space Gamma"""

from mathutils import Vector
import math 
import bpy
import bmesh
import globals as g

class Transformations: #maybe extend blender object or sth better?
    """ collection of transformations of type Transf also containing the representing blender object """
    
    transf_data=[] # will contain the transformations of type Transf
    # passiert hier das gleiche wie mit self.transf_data=[] in __init__?
    
    def __init__(self, signatures=None, plimit = 0.1):
        self.mesh = bpy.data.meshes.new("Transformations")
        self.obj  = bpy.data.objects.new("Transformations", self.mesh)
        self.bm   = bmesh.new()
        if signatures: self.compute(signatures) 
    
    def __getitem__(self, arg): # allows accessing the transf_data directly via []
        return self.transf_data[arg]
        
    def __len__(self):
        return len(self.transf_data)
        
    def add(self, t):
        self.transf_data.append(t)
        self.bm.verts.new(t.co)
    
    def plot(self,scene): # maybe use bmesh edit mode for plotting
        self.bm.to_mesh(self.mesh)
        scene.objects.link(self.obj)
        
    def compute(self,sigs,plimit=0.1):
        """ fills the transformation space with all the transformations (pairing)"""
        
        for i in range(0,len(sigs)):
            # pairing with the followers in the array sorted ! by curvatures
            for j in range(i+1,len(sigs)):
                # skip following signatures, if the curvature differ too much
                if (abs(1 - (sigs[j].curv / sigs[i].curv))) > plimit:
                    break
                # would like to eliminate double entries in signature space before!    
                if (sigs[i].vert.co!=sigs[j].vert.co):                               
                    self.add(Transf(signature1=sigs[i], signature2=sigs[j]))

class Transf:
    """ stores information of a transformation from transformations space """
    def __init__(self,
            signature1=None,signature2=None,
            rnor=None,roff=None,
            co=None):
        """ either compute the transformation between two signatures or create a transformation from rnor, roff """
        if signature1 and signature2:
            self.pc1 = signature1.pc1
            self.pc2 = signature1.pc2
            self.pc = signature1.curv
            self.p = signature1.vert
    
            self.qc1 = signature2.pc1
            self.qc2 = signature2.pc2
            self.qc = signature2.curv
            self.q = signature2.vert
            
            # normal calculation
            self.trans = - self.p.co + self.q.co
            self.rnor = self.trans.normalized()
            # offset calculation in the normal direction
            # = projection of the midpoint in the normal direction
            self.roff = self.rnor * (self.p.co + self.q.co) / 2
            self.calc_co()
            
        elif rnor!=None and roff!=None:
            self.rnor = rnor
            self.roff = roff
            self.calc_co()
        elif co:
            self.co = co
            self.calc_r()
        else:
            raise Exception("Invalid arguments for Transformation")
                
    def calc_co(self):
        self.co = Vector((
                math.atan(self.rnor.y/self.rnor.x) if self.rnor.x != 0 else math.pi/2, #phi
                math.acos(self.rnor.z), #theta
                self.roff)) #off
                
    def calc_r(self):
        self.rnor = Vector((
            math.cos(self.co.x)*math.sin(self.co.y),
            math.sin(self.co.x)*math.sin(self.co.y),
            math.cos(self.co.y)))
        self.roff = self.co.z
    
    def __mul__(self, scalar):
        return Transf(co=self.co*scalar)
    
    def __div__(self, scalar):
        return __mul__(self,(1/scalar))
    
    def __add__(a, b):
        return Transf(co=a.co+b.co)
        
def identity():
    return Transf(rnor=Vector((0,0,1)), roff=0)
    
def d(t1, t2):
    """ metric on the transformation space """
    angle = t1.rnor.angle(t2.rnor)
    angle = min(angle, math.pi - angle)
    offset = abs(t1.roff-t2.roff)
    return angle+offset