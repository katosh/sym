import globals as g

### ANALYSIS -> SIGNATURES ###
class signature:
    id = 0
    co = 0
    normal = 0
    curv = 0
def mksigs():
    for vert in g.bm.verts:
        sig = signature()
        sig.id=vert.index
        sig.co=vert.co
        sig.normal=vert.normal # unfortunately not working (at least in 2d) :(
        sig.curv = vert.calc_shell_factor() # "sharpness of the vertex"
        
        if sig.curv > g.pc:      # Pruning
            g.sigs.append(sig)
        else:
            g.pruned.append(sig)
        
    g.sigs.sort(key=lambda x: x.curv, reverse=False) # sort by curvature
    g.laenge = len(g.sigs) # length of the array
