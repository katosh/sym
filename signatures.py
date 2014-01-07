""" filling the signature space """

import globals as g
import random

class Signature(object):
    """ holds a point together with its carachteristics """
    def __init__(self, vert):
        self.vert = vert
        # TODO: better curvature calculation
        self.curv = vert.calc_shell_factor() # "sharpness of the vertex"
        self.pc1 = None # TODO: principal curvature 1 (vector)
        self.pc2 = None # TODO: principal curvature 2 (vector)

def mksigs():
    """ fill the signature space """
    g.sigs = []
    for vert in g.bm.verts:
        sig = Signature(vert)
        if sig.curv > g.pc and random.random()>0.5:      # Pruning
            g.sigs.append(sig)
        else:
            g.pruned.append(sig)
    g.sigs.sort(key=lambda x: x.curv, reverse=False) # sort by curvature
    g.nsigs = len(g.sigs) # length of the list
