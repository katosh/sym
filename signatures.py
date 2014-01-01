import globals as g

### ANALYSIS -> SIGNATURES ###
class signature():
    curv = 0
    vert = None
def mksigs():
    for vert in g.bm.verts:
        sig = signature()
        sig.vert = vert
        sig.curv = vert.calc_shell_factor() # "sharpness of the vertex"
        
        if sig.curv > g.pc:      # Pruning
            g.sigs.append(sig)
        else:
            g.pruned.append(sig)
        
    g.sigs.sort(key=lambda x: x.curv, reverse=False) # sort by curvature
    g.nsigs = len(g.sigs) # length of the array
