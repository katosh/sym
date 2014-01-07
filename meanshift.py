from mathutils import Vector
import tools

def K(delta,bandwidth):
    return (bandwidth-delta)/bandwidth #hütchenfunktion als kernel

class Cluster:
    def __init__(self, weight, co):
        self.weight = weight

    
def cluster(gamma,steps=100,bandwidth=0.2,densitythreshold=5,offset_threshold=0.001,debug=True):
    clusters=[]
    for t in gamma: #startpunkt
        m=t.co.copy()
        for i in range(steps): #anzahl der shift schritte
            weight=0
            offset=Vector((0,0,0))
            for u in gamma:
                delta = u.co-m
                if 0 < delta.length < bandwidth:
                    offset+=u.co*K(delta.length,bandwidth)
                    weight+=K(delta.length,bandwidth)
            mold=m
            m=(m+offset)/(weight+1)
            if (mold-m).length<offset_threshold:
                break
        if debug and i>steps/2:
            print (i+1,"steps")
        if weight>densitythreshold:
            #print ("shifted",t.co,"to",m,"after",i+1,"steps with an offset of",offset.length,"and a density of",weight)
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