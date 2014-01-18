"""  module for all routines not directly connected to any other modules """

import bmesh
import bpy

def hier_sum(current: list):
    """ hierarchic sum/linear combination of elements """
    length = len(current)
    while length > 1:
        next = []
        for i in range(length//2): # floor division
            next.append(current[2*i] + current[2*i+1])
        if length % 2 == 1:
            next[0] += current[-1]
        current = next
        length = len(current)
    return current[0]

def bmesh_read(obj):
    """ returns a copy of the objects bmesh
        independent of current mode """
    if obj.mode=='EDIT':
        return bmesh.from_edit_mesh(obj.data).copy() # permanent copy
    elif obj.mode=='OBJECT':
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        return bm

def bmesh_write(bmesh, obj):
    """ writes the bmesh to the object
    independent of current mode """
    toggle = False
    if obj.mode == 'EDIT':
        bpy.ops.object.editmode_toggle()
        toggle = True
    bmesh.to_mesh(obj.data)
    if toggle: bpy.ops.object.editmode_toggle()
    # todo: update blender viewport

class Space():
    """ collection of points
        with methods for plotting and selection"""

    def __init__(self):
        self.bm   = bmesh.new()
        self.vertex_dict = {}
        self.elem_dict = {}
        self.elements=[]
        """ size of the space e.g. [pi, pi, max offset difference] """
        self.dimensions = []

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

    def add(self, elem):
        bmvert = self.bm.verts.new(elem.co)
        self.vertex_dict[id(elem)] = bmvert
        self.elem_dict[id(bmvert)] = elem
        self.elements.append(elem)

    def get_bmvert(self, elem):
        return self.vertex_dict[id(elem)]

    def get_elem(self, bmvert):
        return self.elem_dict[id(bmvert)]

    def set_selected(self, elements, exlusive = True, show = True):
        if exlusive:
            for elem in self.elements:
                self.get_bmvert(elem).select = False
        for elem in self.elements:
            self.get_bmvert(elem).select = True
        bmesh_write(self.bm,self.obj)

        if show:
            bpy.context.scene.objects.active = self.obj
            bpy.ops.object.mode_set(mode='EDIT') # doesnt work

    def get_selected(self):
        self.bm = bmesh_read(self.obj)
        # update dictionary

        for elem in self.elements:
            self.vertex_dict[id(elem)] = self.bm.verts[self.get_bmvert(elem).index]
            self.elem_dict[id(self.get_bmvert(elem))] = elem

        selected = []
        for elem in self.elements:
            if self.get_bmvert(elem).select == True:
                selected.append(elem)
        return selected

    def plot(self, scene=bpy.context.scene, label="Space", matrix_world=None):
        self.mesh = bpy.data.meshes.new(label)
        self.obj  = bpy.data.objects.new(label, self.mesh)
        if matrix_world:
            self.obj.matrix_world = matrix_world
        self.bm.verts.index_update() # necessary?
        self.bm.to_mesh(self.mesh)
        scene.objects.link(self.obj)

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
        print('Space dimensions are',self.dimensions)
        for e in self.elements: # necessary?
            e.dimensions = self.dimensions
