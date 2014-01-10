""" filling the signature space """

import random
import bmesh
from sym import get_bmesh

class Signature:
    """ holds a point together with its signature """
    pass

def Signatures(obj,curvpruning=1.5,percentage=0.5):
    """ fill the signature space
        obj: the object to create the signatures of
        curvpruning: the minimal amount of curvature to pass the pruning step
        percentage: the relativy amount of vertices pruned randomly (1 will remove all vertices)"""

    sigs = []
    bm = get_bmesh(obj)

    for vert in obj.data.vertices:
        sig = Signature() # create new signature
        sig.curv = bm.verts[vert.index].calc_shell_factor()
        sig.vert = vert
        if sig.curv > curvpruning and random.random() >= percentage: # Pruning
            sigs.append(sig)
    sigs.sort(key=lambda x: x.curv, reverse=False) # sort by curvature
    return sigs