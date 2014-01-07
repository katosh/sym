from mathutils import Vector
import tools
import transformations

def K(delta,bandwidth):
    return (bandwidth-delta)/bandwidth #hütchenfunktion als kernel

#still not used / implemented    
class Clusters(transformations.Transformations):
    def add(self, t):
        self.transf_data.append(t)
        self.bm.verts.new(t.co)
    
    def plot(self,scene): # maybe use bmesh edit mode for plotting
        self.bm.to_mesh(self.mesh)
        scene.objects.link(self.obj)

    
def cluster(gamma,steps=10,bandwidth=0.5,densitythreshold=3,offset_threshold=0.001,debug=True):
    #clusters=Clusters()
    clusters=[]
    for t in gamma: #startpunkt
        m=t
        for i in range(steps): # maximal count of shift steps to guarantee termination
            weight=1 # not sure whether i shouldnt start with 0
            i=0
            mold=m # save old m to calculate improvement
            for u in gamma:
                dist = transformations.d(u,m)
                if dist < bandwidth:
                    i+=1
                    m      += u*K(dist,bandwidth)
                    weight +=   K(dist,bandwidth)
                    print (u.co,m.co,K(dist,bandwidth))
            print (i)
            m=m*(1/(weight))
            if transformations.d(m,mold)<offset_threshold:
                #break
                pass
        if debug and i>steps/2:
            print (i+1,"steps")
        if weight>densitythreshold:
            found=False
            for c in clusters:
                if transformations.d(c[0],m)<offset_threshold*10: #sonst wird irgendwie nicht gut geclustert...
                    #t.cluster=c
                    found=True
                    break
            if not found:
                clusters.append((m,weight))
                #t.cluster=m
    if debug: print('found',len(clusters),'clusters')
    return clusters
    
def plot_clusters(clusters):
    clustercoords=[]
    for c in clusters:
        clustercoords.append(c[0].co.to_tuple())
    tools.plot_verts("clusters",clustercoords)