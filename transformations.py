""" Pairing and making of the transformation space Gamma"""

import math
import bpy, bmesh
from copy import copy
from mathutils import Vector

import tools

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
            rnor=None, roff=None,
            co=None,
            normalize=True,
            dimensions = [math.pi, math.pi, 1]): # size of Gamma
        """ create a transformation from either two signatures,
        rnor/roff or coordinates in transf. space """
        self.dimensions = dimensions
        if signature1 and signature2:
            self.p = signature1
            self.q = signature2

            co_p = signature1.vert.co
            co_q = signature2.vert.co

            self.trans = - co_p + co_q
            self.rnor = self.trans.normalized()

            # offset calculation in the normal direction
            # = projection of the midpoint in the normal direction
            self.roff = self.rnor * (co_p + co_q) / 2
            self.calc_co()
        elif rnor!=None and roff!=None: # never called
            self.rnor = rnor
            self.roff = roff
            self.calc_co()
        elif co:
            self.co = co
            #self.calc_r not necessary?
        else:
            raise Exception("Invalid arguments for Transformation")

        # further normalizing (restriction on right hemisphere)
        if normalize:
            self.normalize()


    def calc_co(self):
        self.co = Vector((
            math.atan2(self.rnor.y, self.rnor.x), #phi
            math.acos(self.rnor.z), #theta
            self.roff)) #offset

    def apply(self, vec):
        """ takes a vector and returns its reflection"""
        return vec+2*(self.roff - self.rnor*vec)*self.rnor

    def draw(self, scene=bpy.context.scene, maxdensity=None, matrix_world=None):
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
            self.co.y,
            0)
        mesh = bpy.ops.mesh.primitive_plane_add(
                radius=2,
                location = base,
                rotation=n.zyx)
        obj = bpy.context.active_object
        obj.hide = True
        if matrix_world:
            obj.matrix_world = matrix_world * obj.matrix_world
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
            normed = True
        self.calc_r() # necessary?
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
        if t1.rnor is None or t2.rnor is None: # maybe just lazy evaluation?
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
            self.p = signature1
            self.q = signature2

            self.co = - self.p.vert.co + self.q.vert.co
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

def compute(sigs, maxtransformations = 500, group=Reflection):
    """ fills the transformation space
    with all the transformations (pairing)"""

    tfS = tools.Space()
    tfS.d = group.d

    pairs=[]
    for i, a in enumerate(sigs):
        for b in sigs[i+1:]:
            similarity = abs(a.curv - b.curv)
            pair = {'a': a, 'b': b, 'sim': similarity}
            pairs.append(pair)

    pairs.sort(key=lambda x: x['sim'], reverse=False)

    for p in pairs[:maxtransformations]:
        if (p['a'].vert.co != p['b'].vert.co):
            tfS.add(group(signature1=p['a'], signature2=p['b']))

    tfS.find_dimensions()
    return tfS
