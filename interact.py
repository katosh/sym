import sym

def sel_transformations(transformations):
    for t in transformations:
        t.bmvert.select = True
    transformations[0].gamma.set_selection()

def sel_sel_clusters (clusters=None):
    if clusters == None:
        clusters = sym.lastclusters
    clusters.get_selection()
    for c in clusters:
        if c.bmvert.select == True:
            sel_transformations(c.clusterverts)