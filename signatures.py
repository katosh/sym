""" filling the signature space """

import math

class Signature:
    """ holds a point together with its signature """
    def __init__(self, vert):
        """ computes the signature of the vertex vert """ 
        self.vert = vert
        # TODO: better curvature calculation
        self.curv = vert.calc_shell_factor() # "sharpness of the vertex"
        self.pc1 = None # TODO: principal curvature 1 (vector)
        self.pc2 = None # TODO: principal curvature 2 (vector)

def mksigs(verts, maxverts=50):
    """ fill the signature space
        verts: a list of vertices"""

    """ to show the status of the process """
    steps = len(verts) # number of steps
    step = 0 # current step
    waitsteps = math.ceil(steps/1000) # steps befor showing percentage
    slssteps = 0 # steps since last showing of percentage

    sigstemp = []
    for vert in verts:
        sig = Signature(vert)
        sigstemp.append(sig)
        sigstemp.sort(key=lambda x: x.curv, reverse=False) # sort by curvature
        sigs = sigstemp[0:maxverts]

        """ showing process status """
        slssteps += 1
        if slssteps > waitsteps:
            step += slssteps
            print(' process at',math.floor(1000*step/steps)/10,'%', end='\r')
            slssteps = 0
    return sigs
