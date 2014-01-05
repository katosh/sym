from mathutils import Vector


def K(delta,bandwidth):
    return (bandwidth-delta)/bandwidth #hütchenfunktion als kernel
	
def cluster(gamma,steps=20,bandwidth=0.5,densitythreshold=50,offset_threshold=0.01):
	clusters=[]
	for t in gamma: #startpunkt
		m=t.co.copy()
		for i in range(steps): #anzahl der shift schritte
			n=0
			weight=0
			offset=Vector((0,0,0))
			for u in gamma:
				delta = u.co-m
				if 0 < delta.length < bandwidth:
					n+=1
					offset+=delta*K(delta.length,bandwidth)
					weight+=K(delta.length,bandwidth)
			if n==0:
				break
			offset=offset/n
			m+=offset
			if offset.length<offset_threshold:
				break
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
	return clusters