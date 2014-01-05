from mathutils import Vector
import tools

def K(delta,bandwidth):
    return (bandwidth-delta)/bandwidth #hütchenfunktion als kernel
	
def cluster(gamma,steps=100,bandwidth=0.3,densitythreshold=12,offset_threshold=0.01,debug=True):
	clusters=[]
	for t in gamma: #startpunkt
		m=t.co.copy()
		for i in range(steps): #anzahl der shift schritte
			weight=0
			offset=Vector((0,0,0))
			for u in gamma:
				delta = u.co-m
				if 0 < delta.length < bandwidth:
					offset+=delta*K(delta.length,bandwidth)
					weight+=K(delta.length,bandwidth)
			offset=offset/weight
			m+=offset
			if offset.length<offset_threshold:
				break
		if debug and i>steps/2:
			print (i+1,"steps")
		if weight>densitythreshold:
			#print ("shifted",t.co,"to",m,"after",i+1,"steps with an offset of",offset.length,"and a density of",weight)
			found=False
			for cl in clusters:
				if (cl[0]-m).length<offset_threshold*2: #gehört die *2 hier rein?!
					t.cluster=cl
					found=True
					break
			if not found:
				clusters.append((m,weight))
				t.cluster=m
	if debug: print('found',len(clusters),'clusters')
	return clusters
	
def plot_clusters(clusters):
	clustercoords=[]
	for c in clusters:
		clustercoords.append(c[0].to_tuple())
	tools.plot_verts("clusters",clustercoords)