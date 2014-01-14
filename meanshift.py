from __future__ import print_function # overwriting progress status line
from mathutils import Vector
from tools import Space 
from tools import hier_sum
import math
import bpy

def k(delta,bandwidth):
    return (bandwidth-delta)/bandwidth # hütchenfunktion als kernel

def cluster(gamma,
        steps=100,
        bandwidth=0.05,
        densitythreshold=3,
        offset_threshold=0.0001,
        cluster_resolution=0.01,
        grid_size=None,
        progress=True):

    if grid_size is None:
        grid_size = bandwidth / 4

    meanshifts=Space()
    clusters=Space()
    checked=Space()
    track=Space()
    d=gamma.d

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
            sum = []

            for x in gamma:
                dist = d(x, m_old)
                if abs(dist) < bandwidth:
                    x.weight=k(abs(dist), bandwidth)
                    if dist >= 0:
                        sum.append(x*x.weight)
                    else: # just for projective Space
                        sum.append((-x)*x.weight)
                    weight += x.weight

            if i == 0: # save the density of the original point
                g.weight = weight

            if weight != 0:
                m = hier_sum(sum)*(1/weight)
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
        if progress and step % verbosestep == 0:
            print(' process at',"%.1f" % (step/len(gamma)*100),'%', end='\r')


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
                m.clusterverts=Space()
                m.clusterverts.add(m.origin)
                clusters.add(m)

    return clusters, track
