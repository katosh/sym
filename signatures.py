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

    sigS=tools.Space(obj=obj)

    verbosestep = math.ceil(len(sigS)/1000) # steps befor showing percentage

    for step, sig in enumerate(sigS):
        sig.curv = sigS.get_bmvert(sig).calc_shell_factor()
        sig.space = sigS
        # report current progress
        if progress and step % verbosestep == 0:
            print(' process at',"%.1f" % (step/len(sigS)*100),'%', end='\r')

    # the following lines would break sigs beeing of type Space
    # sigstemp.sort(key=lambda x: x.curv, reverse=False) # sort by curvature
    # sigs = sigstemp[0:maxverts]
    return sigS
