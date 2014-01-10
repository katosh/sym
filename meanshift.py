from __future__ import print_function # overwriting proces status line
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
        offset_threshold=0.0001,
        cluster_resolution=0.01):

    meanshifts=Gamma(group=gamma.group)
    clusters=Gamma(group=gamma.group)
    checked=Gamma(group=gamma.group)
    d=gamma.group.d
    #ltrack = Gamma(group=gamma.group) # longest track
    tracks=[] # recording the meanshifts

    #compute meanshift
    steplimit=0

    # show process parameters
    stepss = len(gamma) # number of steps
    step = 0 # current step
    waitsteps = math.ceil(stepss/1000) # steps befor showing percentage
    slssteps = 0 # steps since last showing of percentage

    for g in gamma: # starting point

        # show process
        slssteps += 1
        if slssteps > waitsteps:
            step += slssteps
            print(' process at',math.floor(1000*step/stepss)/10,'%', end='\r')
            slssteps = 0
            
            #print('i jumped',d(m_old,m),'from',
            #        m_old.co,'to',m.co,'to reach the verts')
            #for t in test:
            #    print(t.co,'with weight',t.weight)

        done = False
        for p in checked:
            if abs(d(g,p)) < 0.1:
                done = True
                break
        checked.add(g)
        if done: continue

        m = g
        track=Gamma(group=gamma.group)
        track.add(m)
        for i in range(steps): # maximal count of shift steps to guarantee termination
            weight = 0
            m_old  = m
            # m = gamma.group.id()
            summe = Gamma(group=gamma.group)
            weights = []
            test = Gamma(group=gamma.group)

            for x in gamma:
                dist = d(x, m_old)                
                if abs(dist) < bandwidth:
                    kx = k(abs(dist), bandwidth)
                    x.weight=kx
                    if dist<0:
                        temp = -x
                        temp.weight = -x.weight
                        test.add(temp)
                        summe.add(temp*kx)
                    else:
                        test.add(x)
                        summe.add(x*kx)
                    weights.append(kx)
                    #print ("old",m_old.co,"influenced by",x.co,"with dist",dist, "and weight",k(dist,bandwidth),"to",(m*(1/(weight))).co)
            weight = sum(weights)
            if weight != 0:
                m = summe.summe()*(1/weight)
            else: # there are no more close points which is strange
                m = m_old
                print(step+slssteps,': im lonly')
            normed = m.normalize()
            m.diff = abs(d(m,m_old)) # just for track record

            # tracking the shift
            track.add(m)
            if not normed:
                edge = set(track.bm.verts[j] for j in range(-2,0))
                track.bm.edges.new(edge)

            if abs(d(m,m_old))<offset_threshold: 
                #print(step+slssteps,': i converged')
                break
        if (i==steps-1): 
            steplimit+=1
        m.origin = g
        m.weight = weight
        tracks.append(track)
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
                m.density = m.weight
                m.clusterverts.add(m.origin)               
                clusters.add(m)
    # plot the debugging track
    i=0
    for track in tracks:
        track.plot(bpy.context.scene,label="track"+str(i))
        i += 1
    return clusters
