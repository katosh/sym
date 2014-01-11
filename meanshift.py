from __future__ import print_function # overwriting progress status line
from mathutils import Vector
from transformations import Gamma
import math
import bpy

def k(delta,bandwidth):
    return (bandwidth-delta)/bandwidth # hütchenfunktion als kernel

def cluster(gamma,
        steps=100,
        bandwidth=0.3,
        densitythreshold=5,
        offset_threshold=0.0001,
        cluster_resolution=0.01,
        grid_size=0.1,
        progress=True):

    meanshifts=Gamma(group=gamma.group)
    clusters=Gamma(group=gamma.group)
    checked=Gamma(group=gamma.group)
    track=Gamma(group=gamma.group)
    d=gamma.group.d

    steplimit=0
    verbosestep = math.ceil(len(gamma)/1000) # steps before showing percentage

    # COMPUTE MEANSHIFT

    for step, g in enumerate(gamma): # starting point

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
        for i in range(steps): # maximal count of shift steps to guarantee termination
            weight = 0
            m_old  = m
            summe = Gamma(group=gamma.group)

            for x in gamma:
                dist = d(x, m_old)
                if abs(dist) < bandwidth:
                    kx = k(abs(dist), bandwidth)
                    x.weight=kx
                    if dist >= 0:
                        summe.add(x*kx)
                    else: # just for projective Space
                        summe.add((-x)*kx)
                    weight += kx
            if weight != 0:
                m = summe.summe()*(1/weight)
                checked.add(m)
            else: # there are no more close points which is strange
                print(step,': im lonly')
            normed = m.normalize()

            track.add(m)

            if not normed:
                edge = set(track.bm.verts[j] for j in range(-2,0))
                track.bm.edges.new(edge)

            if abs(d(m,m_old)) < offset_threshold:
                break
        if (i==steps-1):
            steplimit+=1
        m.origin = g
        m.weight = weight
        meanshifts.add(m)

        # report current progress
        if verbose and step % verbosestep == 0:
            print(' process at',"%.1f" % (stepq/len(gamma)*100),'%', end='\r')


    if steplimit > 0: print ("reached mean shift step limit",steplimit," times. consider increasing steps")

    meanshifts.sort(key=lambda x: x.weight, reverse=False)

    # COMPUTE CLUSTERS

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
                m.clusterverts.add(m.origin)
                clusters.add(m)

    return clusters, track
