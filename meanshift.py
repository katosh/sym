from __future__ import print_function # overwriting proces status line
from mathutils import Vector
from transformations import Gamma
import math
import bpy

def k(delta,bandwidth):
    return (bandwidth-delta)/bandwidth # hütchenfunktion als kernel

def cluster(gamma,
        steps=100,
        bandwidth=0.01,
        densitythreshold=5,
        offset_threshold=0.0001,
        cluster_resolution=0.01,
        grid_size=None):

    if grid_size is None:
        grid_size = bandwidth / 4

    meanshifts=Gamma(group=gamma.group)
    clusters=Gamma(group=gamma.group)
    checked=Gamma(group=gamma.group)
    track=Gamma(group=gamma.group)
    d=gamma.group.d

    # compute meanshift
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
            if abs(d(g,p)) < grid_size:
                done = True
                break
        checked.add(g)
        if done: continue

        m = g
        track.add(m)
        last_weight = 1
        for i in range(steps): # maximal count of shift steps to guarantee termination
            weight = 0
            m_old  = m
            # m = gamma.group.id()
            summe = Gamma(group=gamma.group)
            weights = []
            lin_weights = []
            """ exponentponent for the kernel k to sharpen it in dense areas """
            exp = math.log(2/last_weight)/math.log(1/2)
            for x in gamma:
                dist = d(x, m_old)
                if abs(dist) < bandwidth:
                    kx = k(abs(dist), bandwidth)
                    lin_weights.append(kx)
                    x.weight=kx
                    if dist >= 0:
                        summe.add(x*x.weight)
                    else: # just for projective Space
                        temp = -x
                        temp.weight = -x.weight
                        summe.add(temp*x.weight)
                    weights.append(x.weight)
            weight = sum(weights)
            if weight != 0:
                m = summe.summe()*(1/weight)
                checked.add(m)
            else: # there are no more close points which is strange
                m = m_old
                print(step+slssteps,': im lonly')
            normed = m.normalize()
            last_weight = sum(lin_weights)

            # tracking the shift
            track.add(m)

            if not normed:
                edge = set(track.bm.verts[j] for j in range(-2,0))
                track.bm.edges.new(edge)

            if abs(d(m,m_old))<offset_threshold: 
                break
        if (i==steps-1):
            steplimit+=1
        m.origin = g
        m.weight = weight
        meanshifts.add(m)

    if steplimit > 0: print ("reached mean shift step limit",steplimit," times. consider increasing steps")

    meanshifts.sort(key=lambda x: x.weight, reverse=False)

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
                m.clusterverts=Gamma()
                m.density = m.weight
                m.clusterverts.add(m.origin)
                clusters.add(m)
    # plot the debugging track
    track.plot(bpy.context.scene,label="track")
    return clusters
