from mathutils import Vector
from transformations import Gamma
import math
import bpy

def k(delta,bandwidth):
    return (bandwidth-delta)/bandwidth #hütchenfunktion als kernel
    
def cluster(gamma,
        steps=100,
        bandwidth=0.3,
        densitythreshold=5,
        offset_threshold=0.001,
        cluster_resolution=0.01):

    meanshifts=Gamma(group=gamma.group)
    clusters=Gamma(group=gamma.group)
    track=Gamma(group=gamma.group)
    d=gamma.group.d    

    #compute meanshift
    steplimit=0

    # to show status
    stepss = len(gamma) # number of steps
    step = 0 # current step
    waitsteps = math.ceil(stepss/100) # steps befor showing percentage
    slssteps = 0 # steps since last showing of percentage

    for g in gamma: # starting point

        # show status
        slssteps += 1
        if slssteps > waitsteps:
            step += slssteps
            print('process at ',math.floor(100*step/stepss),' %')
            slssteps = 0

        m=g
        for i in range(steps): # maximal count of shift steps to guarantee termination
            weight = 1 # weight of the point itselfe
            """ there semed to be nummercal problems working with the idendity """

            # record particular one track
            if step + slssteps == 330:
                track.add(m)
            m_old  = m

            for x in gamma:
                dist = d(x,m_old)                
                if abs(dist) < bandwidth:
                    kx = k(dist,bandwidth)
                    m       = x*kx + m 
                    weight +=   abs(kx)
                    #print ("old",m_old.co,"influenced by",x.co,"with dist",dist, "and weight",k(dist,bandwidth),"to",(m*(1/(weight))).co)
            m=m*(1/weight)
            m.normalize()
            if abs(d(m,m_old))<offset_threshold: break
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
                if abs(d(c,m)) < cluster_resolution:                    
                    #print ("adding",g,"to cluster",c)
                    found=True
                    c.clusterverts.add(m.origin)
                    break
            if not found:
                #print ("creating cluster at","m")
                m.clusterverts=Gamma()
                m.clusterverts.add(m.origin)               
                clusters.add(m)
    # plot the debugging track
    track.plot(bpy.context.scene,label="track")

    return clusters
