""" filling the signature space """

import bmesh
import math
import bpy

import tools

class Signature:
    """ holds a point together with its signature """
    pass

def Signatures(obj, maxverts = 1000, progress = True):
    """ fill the signature space
        obj: the object to create the signatures of
        curvpruning: the minimal amount of curvature to pass the pruning step
        prune_perc: the relativy amount of vertices pruned randomly (1 will remove all vertices)"""

    bm = tools.bmesh_read(obj)

    verbosestep = math.ceil(len(bm.verts)/1000) # steps befor showing percentage

    sigstemp = []

    for step, vert in enumerate(bm.verts):
        sig = Signature()
        sig.bm = bm # keep copy of bmesh, so it doesnt get destroyed
        sig.vert = vert
        sig.trans = obj.matrix_world
        sig.curv = vert.calc_shell_factor()
        sigstemp.append(sig)
        sigstemp.sort(key=lambda x: x.curv, reverse=False) # sort by curvature
        sigs = sigstemp[0:maxverts]

        # report current progress
        if progress and step % verbosestep == 0:
            print(' process at',"%.1f" % (step/len(gamma)*100),'%', end='\r')
    return sigs

def plot(sigs=None, scene=bpy.context.scene):
    bm = bmesh.new()
    for sig in sigs:
        bm.verts.new(sig.trans * sig.vert.co)
    mesh = bpy.data.meshes.new("sigs")
    obj  = bpy.data.objects.new("sigs", mesh)
    bm.to_mesh(mesh)
    scene.objects.link(obj)
