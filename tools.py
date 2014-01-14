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