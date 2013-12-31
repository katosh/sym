import bpy
import bmesh
import math
from mathutils import Vector
import code
import os
import sys
sys.path.append(r'.')
import globals as g


"""
### Show the mesh in 3-d view
mesh = bpy.data.meshes.new("Buttefly")
g.bm.to_mesh(mesh)
ob_new = bpy.data.objects.new("Butterfly", mesh)     
g.scene.objects.link(ob_new)
"""

import signatures as si
si.mksigs()

import transformations as tr
tr.mktransfs()
tr.plotr()

### CLUSTERING ###



"""------------------------------------------------------------------------- 
				REFLECTION
We generadte a descretazation of the transformation space and call it 'grid'.
We achieve that by first generating a grid over half a unit sphere where
each point represents a direction of a reflectation normal. Then we copy
this hemisphere for each level of reflectation offset to the grid.
Then we calculate the density of transformations for each point of the grid.
-------------------------------------------------------------------------"""
# even point grid on the sphere for clustering of reflection normal direction
# https://perswww.kuleuven.be/~u0017946/publications/Papers97/art97a-Saff-Kuijlaars-MI/Saff-Kuijlaars-MathIntel97.pdf

# adding parameters to our gid vector by estanding the Vector() class
class svector(Vector):  
    dens=0	# add density parameter to Vector()
    roff=0	# add reflectation plane offset

### make hemisphere out of evenly spaced points
Nu = 2*g.mres # resolution / number of directions to analyse weight
sgrid = []	
N=Nu*2
for k in range(Nu,N):   # just halfe shpere since parallel normals are equivalent
    h = -1 + (2*(k-1)/(N-1))
    theta=math.acos(h)
    if k==Nu or k==N:
        phi=0
    else:
        phi=(phi + (3.6/math.sqrt(N*(1-h**2)))) % (2*math.pi) 
    v=svector()
    v.xyz = (math.cos(theta), math.cos(phi)*math.sin(theta), math.sin(phi)*math.sin(theta))
    sgrid.append(v)
# add normals perfectly parallel to axis because such cases ofte ocurr
for i in range(1,4):
    v=svector()
    v.xyz = (i==1,i==2,i==3)
    sgrid.append(v)


### show hemisphere in 3-d view and get faces of sphere-surface for later visualisation
# detour over mesh to create bmesh from a list of vertecis
me = bpy.data.meshes.new("sgrid")        # create a new mesh  
ob = bpy.data.objects.new("sgrid", me)   # create an object with that mesh
me.from_pydata(sgrid,[],[])              # Fill the mesh with verts, edges, faces 
sphere=bmesh.new()
sphere.from_mesh(me)
bmesh.ops.convex_hull(sphere,input=sphere.verts,use_existing_faces=False) # generate faces

# get faces for later visualization
sfaces = []
for f in sphere.faces:
    points=[]
    for v in f.verts:
        points.append(v.index)
    sfaces.append(points)

"""
# show sphere in 3d-view
sphere.to_mesh(me)
bpy.context.g.scene.objects.link(ob)      # Link object to g.scene 
me.update() 
"""

### make grid out of hemisphere and reflectation offset
grid = []
h = g.moff/g.mres	# steps in reflectation offset
for i in range(0,g.mres):
	for v in sgrid:
		v.roff = i*h
		grid.append(v)



# calculate density for each point of the grid
g.ntrans = len(g.transfs)
amw = g.mrad*math.pi		# angle mean width (search radius)
omw = g.mrad*g.moff			# offset mean width (search radius)
for v in grid:
    for t in g.transfs:
        diffa = math.pi - abs(math.pi - v.angle(t.rnor)) # angle between the normals ignoring its sign
        diffo = abs(v.roff - t.roff)	# difference in reflectation offset
        # linear weight looks like __/\__ where amw/omw is the maximal distance
        v.dens += max( 0 , (amw - diffa)/amw + (omw - diffo)/omw)
    v.dens = v.dens/g.ntrans  # normalization

#test = grid.copy()

# show density by hight on the half sphere in 3-d view for the refectations with 0 offset
# transfere data to sgrid

n=0 # offset level (from 0 to g.mres)
for i in range(0,len(sgrid)):
		sgrid[i].dens=grid[i+n*len(sgrid)].dens
#code.interact(local=locals())
model = []
for v in sgrid:
	m = Vector()
	m.xyz = v.xyz*v.dens*10
	model.append(m)    
me = bpy.data.meshes.new("model")       # create a new mesh  
ob = bpy.data.objects.new("model", me)  # create an object with that mesh
g.scene.objects.link(ob)      # Link object to g.scene 
# Fill the mesh with verts, edges, faces 
me.from_pydata(model,[],sfaces)
me.update()  

### VERIFICATION ###
