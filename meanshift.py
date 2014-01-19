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
        densitythreshold=0.01,
        offset_threshold=0.000001,
        cluster_resolution=None,
        grid_size=None,
        progress=True):

    if grid_size is None:
        grid_size = bandwidth / 10

    if cluster_resolution is None:
        cluster_resolution = 2 * grid_size

    meanshifts=Space()
    clusters=Space()
    track=Space()
    d=gamma.d
    grid = dict()

    steplimit=0
    verbosestep = math.ceil(len(gamma)/1000) # steps before showing percentage

    # COMPUTE MEANSHIFT

    for step, g in enumerate(gamma): # starting point
        m = g
        trackl = 0
        track.add(m)

        for i in range(steps): # maximal count of shift steps to guarantee termination
            weight = 0
            sum = []

            if grid_size > 0 and grid_coords(m,grid_size) in grid:
                gridresult = grid[grid_coords(m,grid_size)]
                m = gridresult.copy()
                m.weight = gridresult.weight
                break

            # compute mean-shift step and weights
            for x in gamma:
                dist = d(x, m)
                if abs(dist) < bandwidth:
                    x.weight=k(abs(dist), bandwidth)
                    if dist >= 0:
                        sum.append(x*x.weight)
                    else: # just for projective Space
                        sum.append((-x)*x.weight)
                    weight += x.weight
            if i == 0: # save the density of the original point
                g.weight = weight

            m_old  = m
            m = hier_sum(sum)*(1/weight)
            m.weight = weight

            normed = m.normalize()

            track.add(m)
            trackl += 1
            if not normed:
                edge = set(track.bm.verts[j] for j in range(-2,0))
                track.bm.edges.new(edge)

            if abs(d(m,m_old)) < offset_threshold:
                break

        if grid_size > 0:
            for p in track[-trackl:]:
                grid[grid_coords(p,grid_size)] = m

        m.origin = g
        meanshifts.add(m)

        # report current progress
        if progress and step % verbosestep == 0:
            print(' process at',"%.1f" % (step/len(gamma)*100),'%', end='\r')

        if (i==steps-1):
            steplimit+=1

    if steplimit > 0: print ("reached mean shift step limit",steplimit," times. consider increasing steps")

    meanshifts.sort(key=lambda x: x.weight, reverse=True)

    # COMPUTE CLUSTERS

    for m in meanshifts:
        if m.weight > densitythreshold*meanshifts[0].weight:
            found=False
            for c in clusters:
                if abs(d(c,m)) < cluster_resolution:
                    found=True
                    c.clusterverts.add(m.origin)
                    break
            if not found:
                m.clusterverts=Space()
                m.clusterverts.add(m.origin)
                clusters.add(m)

    return clusters, track

def grid_coords(p, grid_size):
    return tuple([math.floor(c / grid_size) for c in p.co])
