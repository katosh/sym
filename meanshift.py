from __future__ import print_function # overwriting proces status line
from mathutils import Vector
from transformations import Gamma
import math
import bpy
import bmesh
import threading

class Meanshift:

#compute meanshift
    steplimit = 0

    def __init__(self, gamma,
            steps=100,
            bandwidth=0.3,
            densitythreshold=5,
            offset_threshold=0.0001,
            cluster_resolution=0.01,
            grid_size=0.1):
        self.steps = steps
        self.bandwidth = bandwidth
        self.densitythreshold = densitythreshold
        self.offset_threshold = offset_threshold
        self.cluster_resolution = cluster_resolution
        self.grid_size = grid_size
        self.gamma = gamma
        self.meanshifts = Gamma(group=gamma.group)
        self.checked = Gamma(group=gamma.group)
        self.track = bmesh.new()

    def k(self, delta,bandwidth):
        return (bandwidth-delta)/bandwidth #hütchenfunktion als kernel
        
    def cluster(self):
        
        gamma = self.gamma

        """ split gamma in n parts for n threads """
        n = 4 # number of threads
        gammas = []
        for i in range(n):
            gammas.append(Gamma(group=gamma.group))
        i=-1
        for g in gamma:
            i = (i+1) % n
            gammas[i].add(g)

        """ run the mean shift threads """
        stepss = len(gamma) # number of steps
        step = 0 # current step
        waitsteps = math.ceil(stepss/1000) # steps befor showing percentage
        self.slssteps = 0 # steps since last showing of percentage
        self.lock = threading.Lock()
        threads = []
        for gam in gammas:
           thread = threading.Thread(target=self.meanshift, args=([gam]))
           threads.append(thread)
           thread.start()

        """ overhead of threads """
        while True:
            if self.slssteps > waitsteps:
                self.lock.acquire()
                step += self.slssteps
                print(' process at',math.floor(1000*step/stepss)/10,
                        '%', end='\r')
                self.slssteps = 0
                self.lock.release()
            done = True
            for thread in threads:
                if thread.is_alive(): 
                    done = False
                    break
            if done:
                break

        if self.steplimit > 0: print ("reached mean shift step limit",steplimit," times. consider increasing steps")
        
        self.meanshifts.sort(key=lambda x: x.weight, reverse=False)

        """ creating the clusters """
        clusters=Gamma(group=gamma.group)
        d=gamma.group.d
        for m in self.meanshifts:
            if m.weight > self.densitythreshold:
                found=False
                for c in clusters:           
                    if abs(d(c,m)) < self.cluster_resolution:                    
                        #print ("adding",g,"to cluster",c)
                        found=True
                        c.clusterverts.add(m.origin)
                        break
                if not found:
                    m.clusterverts=Gamma()
                    m.density = m.weight
                    m.clusterverts.add(m.origin)               
                    clusters.add(m)
        return clusters

    def meanshift(self, gamma):
        for g in gamma: # starting point

            # show process
            self.lock.acquire()
            self.slssteps += 1
            self.lock.release()

            d=gamma.group.d

            done = False
            self.lock.acquire()
            for p in self.checked:
                if abs(d(g,p)) < self.grid_size:
                    done = True
                    break
            self.checked.add(g)
            trackvert = self.track.verts.new(g.co)
            self.lock.release()
            if done: continue
            m = g
            for i in range(self.steps): # maximal count of shift steps to guarantee termination
                weight = 0
                m_old  = m
                # m = gamma.group.id()
                summe = Gamma(group=gamma.group)
                weights = []

                for x in self.gamma:
                    dist = d(x, m_old)                
                    if abs(dist) < self.bandwidth:
                        kx = self.k(abs(dist), self.bandwidth)
                        x.weight=kx
                        if dist >= 0:
                            summe.add(x*kx)
                        else: # just for projective Space
                            temp = -x
                            temp.weight = -x.weight
                            summe.add(temp*kx)
                        weights.append(kx)
                weight = sum(weights)
                if weight != 0:
                    m = summe.summe()*(1/weight)
                    normed = m.normalize()
                    self.lock.acquire()
                    self.checked.add(m)
                    # tracking the shift
                    trackvert_old = trackvert
                    trackvert = self.track.verts.new(m.co)
                    if not normed:
                        edge = [trackvert_old, trackvert]
                        self.track.edges.new(edge)
                    self.lock.release()
                else: # there are no more close points which is strange
                    m = m_old
                    print(step+slssteps,': im lonly')

                if abs(d(m,m_old))<self.offset_threshold: 
                    break
            if (i==self.steps-1):
                self.lock.acquire()
                self.steplimit+=1
                self.lock.release()
            m.origin = g
            m.weight = weight
            self.lock.acquire()
            self.meanshifts.add(m)
            self.lock.release()

    def plot_tracks(self, track=None, scene=bpy.context.scene):
        """ plot the debugging tracks """
        if track is None:
            track = self.track
        mesh = bpy.data.meshes.new("tracks")
        obj  = bpy.data.objects.new("tracks", mesh)
        track.to_mesh(mesh)
        scene.objects.link(obj)
