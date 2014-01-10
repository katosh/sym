""" Pairing and making of the transformation space Gamma"""

import math 
import bpy, bmesh
from copy import copy
from mathutils import Vector

# everything groupspecific is handled in this
class Reflection:     
    """ class representing the !group of reflections, 
    generating an element from signatures and providing a metric"""
    
    # the points
    p = None
    q = None
    rnor = None
    diff = 0

    def __init__(self,
            signature1=None, signature2=None,
            vert1=None, vert2=None,
            rnor=None, roff=None,
            co=None,
            normalize=True):
        """ create a transformation from either two signatures, 
        rnor/roff or coordinates in transf. space """
        if signature1 and signature2:
            self.p = signature1.vert
            self.q = signature2.vert
        if vert1 and vert2:
            self.p = vert1
            self.q = vert2

        if self.p and self.q:
            self.trans = - self.p.co + self.q.co
            self.rnor = self.trans.normalized()
            # offset calculation in the normal direction
            # = projection of the midpoint in the normal direction
            self.roff = self.rnor * (self.p.co + self.q.co) / 2
            self.calc_co()
            # further normalizing (restriction on right hemisphere)
            if normalize:
                self.normalize()
        elif rnor and roff:
            self.rnor = rnor
            self.roff = roff
            self.calc_r()
            if normalize:
                self.normalize(calc=False)
            else:
                self.calc_co()
        elif co:
            self.co = co
            if normalize:
                self.normalize()
        else:
            raise Exception("Invalid arguments for Transformation")
                

    def draw(self, scene=bpy.context.scene):
        base = self.rnor * self.roff
        rme = bpy.data.meshes.new('rNormal')
        normalverts = [base, base + self.rnor]
        normaledge = [[0, 1]]
        rme.from_pydata(normalverts,normaledge,[])
        ob_normal = bpy.data.objects.new("rNormal", rme)
        scene.objects.link(ob_normal)
        n = Vector() # self rotation in (phi,theta,0)
        n.xyz = (self.co.x,
            self.co.y,
            0)
        bpy.ops.mesh.primitive_plane_add(
                radius=2, 
                location = base, 
                rotation=n.zyx)

    def calc_co(self):
        self.co = Vector((
            math.atan2(self.rnor.y, self.rnor.x), #phi
            math.acos(self.rnor.z), #theta
            self.roff)) #offset
                
    def calc_r(self):
        self.rnor = Vector((
            math.cos(self.co.x)*math.sin(self.co.y),
            math.sin(self.co.x)*math.sin(self.co.y),
            math.cos(self.co.y)))
        self.roff = self.co.z

    def normalize(self):
        """ restriction on one hemisphere """
        normed = False
        if self.co.x > math.pi or self.co.x <= -math.pi:
            self.co.x = (self.co.x + math.pi) % (2*math.pi) -math.pi
            normed = True
        if self.co.y >= math.pi:
            self.co.y = self.co.y % math.pi
            normed = True
        if self.co.x < 0:
            self.co = (-self).co
            self.calc_r()
            normed = True
        return normed

    @staticmethod
    def id():
        return Reflection(co=Vector((0,0,0)))
    
    def __add__(a, b):
        return Reflection(co=a.co+b.co,
                 normalize=False)

    def __sub__(a, b):
        return Reflection(co=a.co-b.co,
                 normalize=False)

    def __neg__(self):
        """ return antipodal point """
        coo=Vector()
        if self.co.x > math.pi/2:
            coo.x = self.co.x -  math.pi
        else:
            coo.x = self.co.x + math.pi
        coo.y = abs(math.pi - self.co.y)
        coo.z = -self.co.z
        return Reflection(co=coo,
                normalize=False)

    def __mul__(self, scalar):
        if scalar < 0: # return antipodal point
            return Reflection(co=-self.co*abs(scalar),
                 normalize=False)
        else:
            return Reflection(co=self.co*scalar,
                 normalize=False)

    def __div__(self, scalar):
        return 1/scalar*self
    
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

    # i know it takes long but its worth it
    @staticmethod
    def d_better_then_real(t1, t2):
        """ metric, if negative -> 
            on oposing hemispheres of sphere,
            distance is then calculated to the antipodal point"""
        if t1.rnor is None:
            t1.calc_r()
        if t2.rnor is None:
            t2.calc_r()
        if t1.co == t2.co:
            return 0
        else:
            angle1 = abs(t1.rnor.angle(t2.rnor))
            angle2 = math.pi - angle1
            if angle1 <= angle2:
                offset = t1.roff-t2.roff
                #da = angle1 * (0.5/(math.pi-angle1+1))
                da = angle1 * (0.5/(math.pi/2 - angle1 + 1))
                return math.sqrt(da**2 + (offset**2))
            else:
                offset = t1.roff+t2.roff
                #da = angle2 * (0.5/(math.pi-angle2+1))
                da = angle2 * (0.5/(math.pi/2 - angle2 + 1))
                return -math.sqrt(da**2 + (offset**2))
        
    d = d_better_then_real
        
class Gamma:
    """ collection of transformations also containing 
    the representing blender object """

    def __init__(self, signatures=None, plimit = 0.1, group=Reflection):
        self.group=group
        self.bm   = bmesh.new()
        self.elements=[]
        if signatures: self.compute(signatures) 
    
    def __getitem__(self, arg): # allows accessing the elements directly via []
        return self.elements[arg]

    def __setitem__(self, arg, item):
        self.elements[arg] = item
        
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

    def summe(self):
        """ hierarchic sum/linear combination of elements """
        length=len(self)
        result = self
        temp = None
        while length > 1:
            temp = Gamma(group=self.group)
            for i in range(math.floor(length/2)):
                temp.add(result[2*i] + result[2*i+1])
            if length % 2 == 1:
                temp[0] = temp[0] + result[length-1]
            result = temp
            length = len(result)
        if result:
            return result[0]
        else:
            return self.group.id()
        
    def compute(self,sigs,plimit=0.1):
        """ fills the transformation space
        with all the transformations (pairing)"""
        for i in range(0,len(sigs)):
            # pairing with the followers in the array sorted by curvatures for pruning!
            for j in range(i+1,len(sigs)):
                # skip following signatures, if the curvature differ too much
                if (abs(1 - (sigs[j].curv / sigs[i].curv))) > plimit:
                    break
                # would like to eliminate double entries in signature space before!
                if (sigs[i].vert.co!=sigs[j].vert.co):
                    self.add(self.group(signature1=sigs[i], signature2=sigs[j]))
