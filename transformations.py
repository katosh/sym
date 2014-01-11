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
            rnor=None, roff=None,
            co=None,
            normalize=True):
        """ create a transformation from either two signatures,
        rnor/roff or coordinates in transf. space """
        if signature1 and signature2:
            self.p = signature1.vert
            self.q = signature2.vert

            self.trans = - self.p.co + self.q.co
            self.rnor = self.trans.normalized()

            # offset calculation in the normal direction
            # = projection of the midpoint in the normal direction
            self.roff = self.rnor * (self.p.co + self.q.co) / 2
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

def computeTransformations(sigs,group=Reflection,prune_curv=0.1):
    transformations=[]
    for i, sig1 in enumerate(sigs):
        for sig2 in sigs[i+1:]:
            # skip following signatures, if the curvature differ too much
            # if curvatures differ to much skip rest
            # requires the sigs to be sorted by curv
            if (abs(1 - (sig2.curv / sig1.curv))) > prune_curv:
                break
            # would like to eliminate double entries in signature space before!
            if (sig1.vert.co!=sig2.vert.co):
                transformations.append(group(signature1=sig1, signature2=sig2))
    return SpacePlot(transformations)

class SpacePlot:
    def __init__(self,elements=None):
        self.elements=[]
        self.bm = bmesh.new()
        self.vertex_dict = {}
        if elements:
            for e in elements:
                self.add(e)
    
    def __getattr__(self, name):
        if name == 'd':
            return self.elements[0].d
                
    def __len__(self):
        return len(self.elements)

    def __iter__(self):
        return iter(self.elements)

    def add(self, elem):
        self.vertex_dict[id(elem)] = self.bm.verts.new(elem.co)
        self.elements.append(elem)

    def plot(self,scene=bpy.context.scene,label="Plot"):
        self.mesh = bpy.data.meshes.new(label)
        self.obj  = bpy.data.objects.new(label, self.mesh)
        scene.objects.link(self.obj)
        self.bm.to_mesh(self.mesh)

    def read_mesh(self):
        self.bm = bmesh.new()
        self.bm.from_mesh(self.obj.data)
        for i, elem in enumerate(elements):
            self.vertex_dict[id(elem)] = self.bm.verts[i]

    def write_mesh(self):
        self.bm.to_mesh(self.mesh)

    def vertex(self, elem):
        return self.vertex_dict[id(elem)]
