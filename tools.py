"""  module for all routines not directly connected to any other modules """

import bmesh

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

def get_bmesh(obj):
    """ returns the BMesh to the object
        choosing the right version depending on current mode """
    #if edit:
    #    bpy.context.scene.objects.active = obj
    #    bpy.ops.object.mode_set(mode='EDIT')
    if obj.mode=='EDIT':
        return bmesh.from_edit_mesh(obj.data)
    elif obj.mode=='OBJECT':
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        return bm
