""" filling the signature space """

import bmesh
import math
import bpy

import tools

class Signature:
    """ holds a point together with its signature """
    pass

def compute(obj, progress = True):
    """ fill the signature space
        obj: the object to create the signatures of
        curvpruning: the minimal amount of curvature to pass the pruning step
        prune_perc: the relativy amount of vertices pruned randomly (1 will remove all vertices)"""

    sigS=tools.Space()
    bm = tools.bmesh_read(obj)

    verbosestep = math.ceil(len(bm.verts)/1000) # steps befor showing percentage

    for step, vert in enumerate(bm.verts):
        sig = Signature()
        sig.bm = bm # keep copy of bmesh, so it doesnt get destroyed
        sig.vert = vert
        sig.co = vert.co
        sig.trans = obj.matrix_world
        sig.curv = vert.calc_shell_factor()
        sigS.add(sig)
        # report current progress
        if progress and step % verbosestep == 0:
            print(' process at',"%.1f" % (step/len(bm.verts)*100),'%', end='\r')

    # the following lines would break sigs beeing of type Space
    # sigstemp.sort(key=lambda x: x.curv, reverse=False) # sort by curvature
    # sigs = sigstemp[0:maxverts]
    return sigS
