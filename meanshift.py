from mathutils import Vector
import tools

def K(delta,bandwidth):
    return (bandwidth-delta)/bandwidth #hütchenfunktion als kernel

class Cluster(Transformations):
    def __init__(self, weight, transf):
        self.weight = weight
        #super.init(self)

    
def cluster(gamma,steps=100,bandwidth=0.2,densitythreshold=5,offset_threshold=0.001,debug=True):
    clusters=[]
    for t in gamma: #startpunkt
        m=t
        for i in range(steps): # maximal count of shift steps to guarantee termination
            weight=0
            offset=transformations.identity()
            mold=m # save old m to calculate improvement
            for u in gamma:
                dist = transformations.d(u,m)
                if dist < bandwidth:
                    m      += u*K(dist,bandwidth)
                    weight +=   K(dist,bandwidth)
            m=m/weight
            if transformations.d(m,mold)<offset_threshold:
                break
        if debug and i>steps/2:
            print (i+1,"steps")
        if weight>densitythreshold:
            found=False
            for cl in clusters:
                if (cl[0]-m).length<offset_threshold*10: #sonst wird irgendwie nicht gut geclustert...
                    t.cluster=cl
                    found=True
                    break
            if not found:
                clusters.append((m,weight))
                t.cluster=m
    if debug: print('found',len(clusters),'clusters')
    return clusters
    
def plot_clusters(clusters):
    clustercoords=[]
    for c in clusters:
        clustercoords.append(c[0].to_tuple())
    tools.plot_verts("clusters",clustercoords)