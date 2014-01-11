from __future__ import print_function # overwriting proces status line
from mathutils import Vector
from transformations import Gamma
import math
import bpy
import bmesh
import time
from multiprocessing import Process, Lock, Pipe

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
        self.track = bmesh.new()

    def cluster(self):
        
        gamma = self.gamma

        """ split gamma in n parts for n procesess
        and select for fairly distant once"""
        n = 4 # number of procesess
        checked = Gamma(group=gamma.group)
        gammas = []
        d=gamma.group.d
        for i in range(n):
            gammas.append(Gamma(group=gamma.group))
        i=-1
        for g in gamma:
            too_close = False
            for c in checked:
                if abs(d(c,g)) < self.grid_size:
                    too_close = True
                    break
            if not too_close:
                i = (i+1) % n
                gammas[i].add(g)
                checked.add(g)

        """ make the pipes and run the mean shift processes """
        stepss = len(checked) # number of steps
        lock = Lock()
        processes = []
        pipes = []
        slssteps, statuspipe_child = Pipe()# steps since last showing of percentage
        for gam in gammas:
            parent_conn, child_conn = Pipe()
            process = Process(target=ShiftingProcess.meanshift, args=(
                    gamma,
                    gam,
                    self.bandwidth,
                    self.offset_threshold,
                    self.steps,
                    statuspipe_child,
                    lock,
                    child_conn))
            processes.append(process)
            pipes.append(parent_conn)
            process.start()

        """ overhead of processes """
        step = 0 # current step
        waitsteps = math.ceil(stepss/1000) # steps befor showing percentage
        while True:
            time.sleep(1)
            #if slssteps.recv()[0] > waitsteps:
            #    lock.acquire()
            #    step += slssteps.recv()[0]
            #    print(' process at',math.floor(1000*step/stepss)/10,
            #            '%', end='\r')
            #    slssteps.send([0])[0]
            #    lock.release()
            done = True
            for process in processes:
                if process.is_alive(): 
                    done = False
                    break
            if done:
                break

        """ collection the results of the procesess """
        self.track = None
        for pipe in pipes:
            [ms, steplim, tr] = pipe.recv()
            for m in ms:
                self.meanshift.add(m)
            self.steplimit += steplim
            for t in tr:
                mesh = bpy.data.meshes.new("track")
                t.to_mesh(mesh)
                obj = bpy.data.objects.new("tracks", mesh)
                if self.track is None:
                    self.track = obj
                else:
                    self.track.join(obj)

        if self.steplimit > 0: print ("reached mean shift step limit",
                self.steplimit," times. consider increasing steps")
        
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


    def plot_tracks(self, track=None, scene=bpy.context.scene):
        """ plot the debugging tracks """
        if track is None:
            track = slef.track
        mesh = bpy.data.meshes.new("tracks")
        obj  = bpy.data.objects.new("tracks", mesh)
        track.to_mesh(mesh)
        scene.objects.link(obj)

class ShiftingProcess:

    @staticmethod
    def k(delta,bandwidth):
        return (bandwidth-delta)/bandwidth #hütchenfunktion als kernel
    
    @staticmethod 
    def meanshift(
            gamma_whole,
            gamma,
            bandwidth,
            offset_threshold,
            steps,
            slssteps,
            lock,
            my_output):

        track = bmesh.new()
        steplimit = 0
        meanshift = Gamma(group=gamma.group)

        for g in gamma: # starting point
            d=gamma.group.d
            m = g
            for i in range(steps): # maximal count of shift steps to guarantee termination
                weight = 0
                m_old  = m
                summe = Gamma(group=gamma.group)
                weights = []
                trackvert = track.verts.new(m.co) # tracking the shift

                for x in gamma_whole:
                    dist = d(x, m_old)                
                    if abs(dist) < bandwidth:
                        kx = ShiftingProcess.k(abs(dist), bandwidth)
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
                    # tracking the shift
                    trackvert_old = trackvert
                    trackvert = track.verts.new(m.co)
                    if not normed:
                        edge = [trackvert_old, trackvert]
                        track.edges.new(edge)
                else: # there are no more close points which is strange
                    m = m_old
                    print(step+slssteps,': im lonly')

                if abs(d(m,m_old))<offset_threshold: 
                    break
            if (i==steps-1):
                steplimit+=1
            m.origin = g
            m.weight = weight
            meanshift.add(m)
            
            # show process
            #lock.acquire()
            #slssteps.send([slssteps.recv()[0] + 1])
            #lock.release()
        my_output.send([meanshift, steplimit, track])
