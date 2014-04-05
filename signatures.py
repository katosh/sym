""" filling the signature space """

import bmesh
import sym
import math
import bpy

class Signature:
    """ holds a point together with its signature """
    pass

def Signatures(obj, maxverts = 1000):
    """ fill the signature space
        obj: the object to create the signatures of
        curvpruning: the minimal amount of curvature to pass the pruning step
        prune_perc: the relativy amount of vertices pruned randomly (1 will remove all vertices)"""

    verts = obj.data.vertices

    """ to show the status of the process """
    steps = len(verts) # number of steps
    step = 0 # current step
    waitsteps = math.ceil(steps/1000) # steps befor showing percentage
    slssteps = 0 # steps since last showing of percentage

    top = math.floor(steps*0.02) # top 2%

    sigstemp = []
    bm = sym.get_bmesh(obj)
    for vert in verts:
        sig = Signature()
        sig.vert = vert
        sig.trans = obj.matrix_world
        sig.curv = bm.verts[vert.index].calc_shell_factor()
        sigstemp.append(sig)

        """ showing process status """
        slssteps += 1
        if slssteps > waitsteps:
            step += slssteps
            print(' process at',math.floor(1000*step/steps)/10,'%', end='\r')
            slssteps = 0

    sigstemp.sort(key=lambda x: x.curv, reverse=False) # sort by curvature
    sigs = sigstemp[top:maxverts+top]
    return sigs

def plot(sigs=None, scene=bpy.context.scene):
    bm = bmesh.new()
    for sig in sigs:
        bm.verts.new(sig.trans * sig.vert.co)
    mesh = bpy.data.meshes.new("sigs")
    obj  = bpy.data.objects.new("sigs", mesh)
    bm.to_mesh(mesh)
    scene.objects.link(obj)
