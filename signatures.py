import globals as g

### ANALYSIS -> SIGNATURES ###
class signature():
    def __init__(self, vertex = None):
        self.vert = vertex
        # TODO: better curvature calculation
        self.curv = vertex.calc_shell_factor() # "sharpness of the vertex"
        self.pc1 = None # TODO: principal curvature 1 (vector)
        self.pc2 = None # TODO: principal curvature 2 (vector)
def mksigs():
    for vert in g.bm.verts:
        sig = signature(vertex=vert)
        if sig.curv > g.pc:      # Pruning
            g.sigs.append(sig)
        else:
            g.pruned.append(sig)
        
    g.sigs.sort(key=lambda x: x.curv, reverse=False) # sort by curvature
    g.nsigs = len(g.sigs) # length of the list
