from mathutils import Vector
from transformations import Gamma

def k(delta,bandwidth):
    return (bandwidth-delta)/bandwidth #hütchenfunktion als kernel
    
def cluster(gamma,steps=100,bandwidth=0.3,densitythreshold=2,offset_threshold=0.001,cluster_resolution=0.01):

    meanshifts=Gamma(group=gamma.group)
    clusters=Gamma(group=gamma.group)
    d=gamma.group.d    
    
    #compute meanshift
    steplimit=0
    for g in gamma: # starting point
        m=g
        for i in range(steps): # maximal count of shift steps to guarantee termination
            weight=1 # not sure whether i shouldnt start with 0
            m_old=m # save old m to calculate improvement
            for x in gamma:
                dist = d(x,m)
                if dist < bandwidth:
                    m      += x*k(dist,bandwidth)
                    weight +=   k(dist,bandwidth)
                    #print ("old",m_old.co,"influenced by",x.co,"with dist",dist, "and weight",k(dist,bandwidth),"to",(m*(1/(weight))).co)
            m=m*(1/(weight))
            if d(m,m_old)<offset_threshold: break
            
        if (i==steps-1): steplimit+=1
        m.origin=g
        m.weight=weight
        meanshifts.add(m)
        
    if steplimit > 0: print ("reached mean shift step limit",steplimit," times. consider increasing steps")
    
    # todo: sort meanshifts by weights...
    
    # create clusters   
    for m in meanshifts:
        if m.weight > densitythreshold:
            found=False
            for c in clusters:           
                if d(c,m) < cluster_resolution:                    
                    #print ("adding",g,"to cluster",c)
                    found=True
                    c.clusterverts.add(m.origin)
                    break
            if not found:
                #print ("creating cluster at","m")
                m.clusterverts=Gamma()
                m.clusterverts.add(m.origin)               
                clusters.add(m)

    return clusters