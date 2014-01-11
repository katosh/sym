from __future__ import print_function # overwriting progress status line
from mathutils import Vector
from transformations import SpacePlot
import math
import bpy

def k(delta,bandwidth):
    return (bandwidth-delta)/bandwidth # hütchenfunktion als kernel

def meanshift(gamma,
        steps=100,
        bandwidth=0.3,
        densitythreshold=5,
        offset_threshold=0.0001,
        cluster_resolution=0.01,
        verbose=True,**args):
    
    d=gamma.d
    meanshifts=[]
    traces=SpacePlot() # tracing each meanshift

    steplimit_reached = 0

    verbosestep = math.ceil(len(gamma)/1000) # steps before showing percentage
 
    ### MEANSHIFTING ###
 
    for step, g in enumerate(gamma):
        m = g
        traces.add(m)
        for i in range(steps): # maximal count of shift steps to guarantee termination
            weight = 0
            m_old  = m
            summe = []
            weights = []

            for x in gamma:
                dist = d(m_old, x)
                if abs(dist) < bandwidth:
                    kx = k(abs(dist), bandwidth)
                    if dist>0:
                        m=m+(x*kx)
                    else: # can happen for Reflections, add antipodal point
                        m=m+((-x)*kx)   
                    weight += kx

            if weight != 0:
                m = m*(1/weight)
            else: # there are no more close points which is strange
                print(step,': im lonly')
            
            normed = m.normalize()

            # tracing            
            traces.add(m)
            if not normed:
                edge = set(traces.bm.verts[j] for j in range(-2,0))
                traces.bm.edges.new(edge)
                
            # if converged break
            if abs(d(m,m_old))<offset_threshold:
                break
        
        # count how many times we reached the steplimit    
        if (i==steps-1):
            steplimit_reached+=1
            
        m.origin = g
        m.weight = weight
        meanshifts.append(m)
        
        if verbose and step % verbosestep == 0:
            print(' process at',"%5.1f" % (step/len(gamma)*100),'%', end='\r')

    if steplimit_reached > 0: 
        print ("reached mean shift step limit",steplimit_reached," times. consider increasing steps")

    # todo: sort meanshifts by weights...
    
    ### CLUSTERING ###
    
    clusters=SpacePlot()
    for m in meanshifts:
        if m.weight > densitythreshold:
            found=False
            for c in clusters:
                if abs(d(c,m)) < cluster_resolution:
                    found=True
                    c.clusterverts.append(m.origin)
                    break
            if not found:
                m.clusterverts=[]
                m.clusterverts.append(m.origin)
                clusters.add(m)
    return clusters, traces
