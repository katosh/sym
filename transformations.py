""" Pairing and making of the transformation space Gamma"""

import math
import bpy, bmesh
from copy import copy
from mathutils import Vector

# everything groupspecific is handled in this
class Reflection:
    """ class representing the !group of reflections,
    generating an element from signatures and providing a metric"""

    p = None
    q = None
    rnor = None
    diff = None

    def __init__(self,
            signature1=None, signature2=None,
            vert1=None, vert2=None,
            real_co1=None, real_co2=None,
            rnor=None, roff=None,
            co=None,
            normalize=True,
            dimensions = [math.pi, math.pi, 1]): # size of Gamma
        """ create a transformation from either two signatures,
        rnor/roff or coordinates in transf. space """
        self.dimensions = dimensions
        if signature1 and signature2:
            self.p = signature1.vert
            self.q = signature2.vert

            if real_co1 and real_co2:
                p_real_co = real_co1
                q_real_co = real_co2
            else:
                p_real_co = signature1.trans * signature1.vert.co
                q_real_co = signature2.trans * signature2.vert.co 

            self.trans = - p_real_co + q_real_co
            self.rnor = self.trans.normalized()

            # offset calculation in the normal direction
            # = projection of the midpoint in the normal direction
            self.roff = self.rnor * (p_real_co + q_real_co) / 2
            self.calc_co()

            # further normalizing (restriction on right hemisphere)
            if normalize:
                self.normalize()

        elif rnor!=None and roff!=None:
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

    def calc_co(self):
        self.co = Vector((
            math.atan2(self.rnor.y, self.rnor.x), #phi
            math.acos(self.rnor.z), #theta
            self.roff)) #offset

    def draw(self, scene=bpy.context.scene, maxdensity=None):
        """ draws the reflection plane in the scene """
        base = self.rnor * self.roff
        #rme = bpy.data.meshes.new('rNormal')
        #normalverts = [base, base + self.rnor]
        #normaledge = [[0, 1]]
        #rme.from_pydata(normalverts,normaledge,[])
        #ob_normal = bpy.data.objects.new("rNormal", rme)
        #scene.objects.link(ob_normal)
        n = Vector() # self rotation in (phi,theta,0)
        n.xyz = (self.co.x,
            -self.co.y,
            0)
        mesh = bpy.ops.mesh.primitive_plane_add(
                radius=2,
                location = base,
                rotation=n.zyx)
        obj = bpy.context.active_object
        obj.hide = True
        if maxdensity:
            material = bpy.data.materials.new('color')
            material.diffuse_color = (self.weight/maxdensity, 
                    1 - self.weight/maxdensity, 
                    1 - self.weight/maxdensity)
            mesh = obj.data
            mesh.materials.append(material)

    def calc_r(self):
        self.rnor = Vector((
            math.cos(self.co.x)*math.sin(self.co.y),
            math.sin(self.co.x)*math.sin(self.co.y),
            math.cos(self.co.y)))
        self.roff = self.co.z

    @staticmethod
    def id():
        return Reflection(co=Vector((0,0,0)))

    def normalize(self):
        """ restriction on one hemisphere """
        normed = False
        if self.co.x > math.pi or self.co.x <= -math.pi:
            self.co.x = (self.co.x + math.pi  % (2*math.pi)) - math.pi
            normed = True
        if self.co.y >= math.pi:
            self.co.y = self.co.y % math.pi
            normed = True
        if self.co.x < -math.pi/2 or self.co.x >= math.pi/2:
            self.co = (-self).co
            self.calc_r()
            normed = True
        return normed

    def __add__(a, b):
        return Reflection(co=a.co+b.co,
                 normalize=False)

    def __sub__(a, b):
        return Reflection(co=a.co-b.co,
                 normalize=False)

    def __neg__(self):
        """ return antipodal point """
        coo=Vector()
        if self.co.x > 0:
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
        factor = 1 / t1.dimensions[2] # scaling for offset distance
        if t1.rnor is None or t2.rnor is None:
            t1.calc_r()
        if t1.co == t2.co:
            return 0
        else:
            angle1 = abs(t1.rnor.angle(t2.rnor))
            angle2 = math.pi - angle1
            if angle1 <= angle2:
                offset = (t1.roff-t2.roff) * factor
                #da = angle1 * (math.pi/(2*(math.pi - angle1 + 1)))
                da = angle1/math.pi/2
                return math.sqrt(da**2 + (offset**2))
            else:
                offset = (t1.roff+t2.roff) * factor
                #da = angle2 * (math.pi/(2*(math.pi - angle2 + 1)))
                da = angle2/math.pi/2
                return -math.sqrt(da**2 + (offset**2))

    d = d_better_then_real

class Translation:
    """ class representing the !group of reflections, generating an element from signatures and providing a metric"""

    def __init__(self,
            signature1=None,signature2=None,
            co=None):
        """ create a transformation from either two signatures, rnor/roff or coordinates in transf. space """
        if signature1 and signature2:
            self.p = signature1.vert
            self.q = signature2.vert

            self.co = - self.p.co + self.q.co
        elif co:
            self.co = co
        else:
            raise Exception("Invalid arguments for Transformation")

    def id():
        return Translation(co=Vector((0,0,0)))

    def __mul__(self, scalar):
        return Reflection(co=self.co*scalar)

    def __add__(a, b):
        return Reflection(co=a.co+b.co)

    @staticmethod
    def d(t1, t2):
        return (t1.co-t2.co).length

class Gamma:
    """ collection of transformations also containing
    the representing blender object """

    def __init__(self, signatures=None, plimit = 0.1, group=Reflection):
        self.group=group
        self.bm   = bmesh.new()
        self.elements=[]
        """ size of the space e.g. [pi, pi, max offset difference] """
        self.dimensions = []
        if signatures: self.compute(signatures)

    def __getitem__(self, arg): # allows accessing the elements directly via []
        return self.elements[arg]

    def __setitem__(self, arg, item):
        self.elements[arg] = item

    def __len__(self):
        return len(self.elements)

    def __iter__(self):
        return iter(self.elements)

    def sort(self,**kwargs):
        self.elements.sort(**kwargs)

    def add(self, tf):
        tf.bmvert = self.bm.verts.new(tf.co)
        if not hasattr(tf,'index'): tf.index=len(self.elements)
        if not hasattr(tf,'gamma'): tf.gamma=self
        self.elements.append(tf)

    def plot(self,scene,label="Plot"):
        self.mesh = bpy.data.meshes.new(label)
        self.obj  = bpy.data.objects.new(label, self.mesh)
        self.bm.verts.index_update()
        self.bm.to_mesh(self.mesh)
        scene.objects.link(self.obj)

    def compute(self, sigs, maxtransformations = 500):
        """ fills the transformation space
        with all the transformations (pairing)"""
        class pair:
            def __init__(self):
                self.a = None
                self.b = None
                self.similarity = 0
        pairs = []
        for i in range(0,len(sigs)):
            for j in range(i+1,len(sigs)):
                p = pair()
                p.a = sigs[j]
                p.b = sigs[i]
                p.similarity = abs(sigs[j].curv - sigs[i].curv)
                pairs.append(p)
        """ sorting the pairs by similarity """
        pairs.sort(key=lambda x: x.similarity, reverse=False)
        """ adding maxtransformation many to the space """
        for i in range(min(maxtransformations, len(pairs))):
            a_real_co = pairs[i].a.vert.co * pairs[i].a.trans
            b_real_co = pairs[i].b.vert.co * pairs[i].b.trans
            if (a_real_co != b_real_co):
                self.add(self.group(signature1=pairs[i].a,
                        signature2=pairs[i].b,
                        real_co1=a_real_co,
                        real_co2=b_real_co))
        self.find_dimensions()

    def find_dimensions(self):
        minv = []
        maxv = []
        for e in self.elements:
            i = 0
            for x in e.co:
                if i == len(minv):
                    minv.append(x)
                    maxv.append(x)
                else:
                    minv[i] = min(minv[i], x)
                    maxv[i] = max(maxv[i], x)
                i += 1
        for i in range(len(minv)):
            self.dimensions.append(maxv[i] - minv[i])
        print('Gammas dimensions are',self.dimensions)
        for e in self.elements:
            e.dimensions = self.dimensions
