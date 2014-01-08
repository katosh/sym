""" Pairing and making of the transformation space Gamma"""

import math 
import bpy, bmesh
from mathutils import Vector

# everything groupspecific is handled in this
class Reflection:     
    """ class representing the !group of reflections, generating an element from signatures and providing a metric"""
    
    def __init__(self,
            signature1=None,signature2=None,
            rnor=None,roff=None,
            co=None):
        """ create a transformation from either two signatures, rnor/roff or coordinates in transf. space """
        if signature1 and signature2:
            self.p = signature1.vert
            self.q = signature2.vert
            
            self.trans = - self.p.co + self.q.co
            self.rnor = self.trans.normalized()
            
            # offset calculation in the normal direction
            # = projection of the midpoint in the normal direction
            self.roff = self.rnor * (self.p.co + self.q.co) / 2
            # further normalizing
            if self.p.co.x < 0:
                self.p = signature2.vert
                self.q = signature1.vert
                self.rnor = -self.rnor
                self.roff = -self.roff
            self.calc_co()
            
        elif rnor and roff:
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
        
    def id():
        return Reflection(co=Vector((0,0,0)))
    
    def __mul__(self, scalar): # todo: fix
        return Reflection(co=self.co*scalar)
    
    def __add__(a, b): # todo: fix
        return Reflection(co=a.co+b.co)
    
    @staticmethod
    def d_real(t1, t2): # most timeintensive function of the code so far... around 50% of time just for this
        """ metric on the reflection space """
        angle = t1.rnor.angle(t2.rnor)
        angle = min(angle, math.pi - angle)
        offset = abs(t1.roff-t2.roff)
        return angle+offset
        
    @staticmethod
    def d_fake(t1, t2):
        return (t1.co-t2.co).length
        
    d = d_fake
        
class Gamma:
    """ collection of transformations also containing the representing blender object """

    def __init__(self, signatures=None, plimit = 0.1, group=Reflection):
        self.group=group
        self.bm   = bmesh.new()
        self.elements=[]
        if signatures: self.compute(signatures) 
    
    def __getitem__(self, arg): # allows accessing the elements directly via []
        return self.elements[arg]
        
    def __len__(self):
        return len(self.elements)
        
    def __iter__(self):
        return iter(self.elements)
        
    def add(self, tf):
        tf.bmvert = self.bm.verts.new(tf.co)
        self.elements.append(tf)        
    
    def plot(self,scene,label="Plot"):
        self.mesh = bpy.data.meshes.new(label)
        self.obj  = bpy.data.objects.new(label, self.mesh)
        self.bm.to_mesh(self.mesh)
        scene.objects.link(self.obj)
        
    def compute(self,sigs,plimit=0.1):
        """ fills the transformation space with all the transformations (pairing)"""        
        for i in range(0,len(sigs)):
            # pairing with the followers in the array sorted by curvatures for pruning!
            for j in range(i+1,len(sigs)):
                # skip following signatures, if the curvature differ too much
                if (abs(1 - (sigs[j].curv / sigs[i].curv))) > plimit:
                    break
                # would like to eliminate double entries in signature space before!    
                if (sigs[i].vert.co!=sigs[j].vert.co):
                    self.add(self.group(signature1=sigs[i], signature2=sigs[j]))
