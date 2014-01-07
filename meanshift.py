from mathutils import Vector
from transformations import Gamma

def k(delta,bandwidth):
    return (bandwidth-delta)/bandwidth #hütchenfunktion als kernel
    
def cluster(gamma,steps=100,bandwidth=0.2,densitythreshold=1.2,offset_threshold=0.001,cluster_resolution=0.1):
    clusters=Gamma(group=gamma.group)
    d=gamma.group.d
    steplimit=0
    for t in gamma.elements: # starting point
        
        #compute meanshift
        m=t
        for i in range(steps): # maximal count of shift steps to guarantee termination
            weight=1 # not sure whether i shouldnt start with 0
            m_old=m # save old m to calculate improvement
            for u in gamma:
                dist = d(u,m)
                if dist < bandwidth:
                    m      += u*k(dist,bandwidth)
                    weight +=   k(dist,bandwidth)
                    #print ("old",m_old.co,"influenced by",u.co,"with dist",dist, "and weight",k(dist,bandwidth),"to",(m*(1/(weight))).co)
            m=m*(1/(weight))
            if d(m,m_old)<offset_threshold:
                break

        if (i==steps-1): steplimit+=1 
        
        # add to cluster
        if weight > densitythreshold:           
            found=False
            for c in clusters.elements:           
                if d(c,m) < cluster_resolution:                    
                    #print ("adding",t,"to cluster",c)
                    found=True
                    c.clusterverts.add(t)
                    break
            if not found:
                #print ("creating cluster at","m")
                m.weight=weight
                m.clusterverts=Gamma()
                m.clusterverts.add(t)                
                clusters.add(m)
    if steplimit>0: print ("reached mean shift step limit",steplimit," times. consider increasing steps")
    return clusters