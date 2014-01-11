""" filling the signature space """

import random

class Signature:
    """ holds a point together with its signature """
    def __init__(self, vert):
        """ computes the signature of the vertex vert """ 
        self.vert = vert
        # TODO: better curvature calculation
        self.curv = vert.calc_shell_factor() # "sharpness of the vertex"
        self.pc1 = None # TODO: principal curvature 1 (vector)
        self.pc2 = None # TODO: principal curvature 2 (vector)

def mksigs(verts,curvpruning=1.5, percentage=0):
    """ fill the signature space
        verts: a list of vertices
        curvpruning: the minimal amount of curvature to pass the pruning step
        percentage: the relativy amount of vertices pruned randomly (1 will remove all vertices)"""
    sigs = []
    for vert in verts:
        sig = Signature(vert)
        if sig.curv > curvpruning and random.random() >= percentage:      # Pruning
            sigs.append(sig)
    sigs.sort(key=lambda x: x.curv, reverse=False) # sort by curvature
    return sigs
