import bpy
import bmesh
import math
from mathutils import Vector
bmesh.types.BMesh.free
import globals as g

### for visualization
sphere = bmesh.new()    # one layer offsel layer of reflectation grid
me = bpy.data.meshes.new("mymesh")          # create a new mesh  
ob = bpy.data.objects.new("myobject", me)   # create an object with that mesh

### CLUSTERING ###

"""------------------------------------------------------------------------- 
				REFLECTION
We generadte a descretazation of the transformation space and call it 'grid'.
We achieve that by first generating a grid over half a unit sphere where
each point represents a direction of a reflectation normal. Then we copy
this hemisphere for each level of reflectation offset to the grid.
Then we calculate the density of transformations for each point of the grid.
-------------------------------------------------------------------------"""

# adding parameters to our gid vector by extanding the Vector() class
class svector(Vector):  
    dens=0	# add density parameter to Vector()
    roff=0	# add reflectation plane offset

def mkrgrid():  # make grid for reflection space
    # even point grid on the sphere for clustering 
    # of reflection normal direction
    # https://perswww.kuleuven.be/~u0017946/publications/Papers97/art97a-Saff-Kuijlaars-MI/Saff-Kuijlaars-MathIntel97.pdf

    ### make hemisphere out of evenly spaced points
    Nu = 2*g.mres # resolution / number of directions to analyse weight
    N=Nu*2
    # generate just a halfe shpere since parallel normals are equivalent
    for k in range(Nu,N): 
        h = -1 + (2*(k-1)/(N-1))
        theta=math.acos(h)
        if k==Nu or k==N:
            phi=0
        else:
            phi=(phi + (3.6/math.sqrt(N*(1-h**2)))) % (2*math.pi) 
        v=svector()
        v.xyz = (math.cos(theta), 
                math.cos(phi)*math.sin(theta), 
                math.sin(phi)*math.sin(theta))
        g.rsgrid.append(v)
    # add normals perfectly parallel to axis because such cases ofte ocurr
    for i in range(1,4):
        v=svector()
        v.xyz = (i==1,i==2,i==3)
        g.rsgrid.append(v)


    ### show hemisphere in 3-d view and 
    ### get faces of sphere-surface for later visualisation
    # detour over mesh to create bmesh from a list of vertecis
    global sphere
    global me
    me.from_pydata(g.rsgrid,[],[]) # Fill the mesh with verts, edges, faces 
    sphere.from_mesh(me)
    # generate faces
    bmesh.ops.convex_hull(sphere,input=sphere.verts,use_existing_faces=False) 

    # get faces for later visualization
    for f in sphere.faces:
        points=[]
        for v in f.verts:
            points.append(v.index)
        g.sfaces.append(points)

    ### make grid out of hemisphere and reflectation offset
    h = (g.moff-g.mioff)/g.mres	# steps in reflectation offset
    for i in range(0,g.mres):
        for v in g.rsgrid:
            v.roff = i*h + g.mioff
            g.rgrid.append(v)

#### show sphere in 3d-view
def showhemisphere():
    global me
    sphere.to_mesh(me)
    g.scene.objects.link(ob)      # Link object to g.scene 
    me.update() 


class Maximum:
    def __init__(self, 
            transformation=None, 
            gridpoint=None, 
            weight=0, 
            distance=0):
        self.grid = gridpoint
        self.t = transformation
        # distance/difference between gridpoint and actual tarnsformation
        self.dist = distance 
        self.weight = weight  # weight in density function

mt = Maximum()  # saves best transformation for a grid point
m1 = Maximum()  # holds one maximum

### mean shift for reflectation space
def rmeanshift():
    # calculate density for each point of the grid
    global m1
     # length of space diagonal; also the maximal distance to any grid point
    diag = math.sqrt((math.pi**2)+((g.moff-g.mioff)**2))
    msr = g.mrad*diag # mean shift search radius
    for v in g.rgrid:
        v.dens = 0
        mt
        closest = 0
        for t in g.transfs:
            # angle to the normals ignoring there sign
            diffa = min(v.angle(t.rnor), math.pi - v.angle(t.rnor))
            # difference in reflectation offset
            diffo = abs(v.roff - t.roff)
            diff = math.sqrt((diffa**2)+(diffo**2))
            # linear weight looks like __/\__ 
            weight = (msr - diff)/msr
            v.dens += max(0,weight)
            # v.dens += max(0, 1 - (diffa/amw) - (diffo/omw))
            # v.dens += max( 0 , (amw - diffa)/amw)   # ignoring offset
            if mt.dist is None:
                mt.dist = diff
            if diff < mt.dist:
                mt.t = t
                mt.dist = diff
                mt.weight = weight 
        v.dens = v.dens/g.ntransfs  # normalization
        if v.dens > m1.grid.dens:
            m1.t = mt.t
            m1.dist = mt.dist
            m1.weight = mt.weight
            m1.grid = v
    g.bref = m1.t # safe best reflection transformation

### show offset layer with maximum
def showmrlayer():
    n = round((m1.grid.roff/g.moff)*g.mres)
    showrlayer(n)
    print('highest density at an offset of ',m1.grid.roff)
    print('this is level ',n,' of ',g.mres)
    print('the maximal offset is ',g.moff)
    print('the minimal offset is ',g.mioff)
    print('the reflection normal is ',m1.t.rnor)
    print('the number of transformations is ',g.ntransfs)
    print('the highes density is ',m1.grid.dens)
    print('the best transformation is between the points ',
            m1.t.p.co,' and ',m1.t.q.co,
            ' with the indices ',m1.t.p.index,' and ',m1.t.q.index)

### show density by hight on the hemisphere 
### in 3-d view for the refectations on offset layer n
def showrlayer(n):
    # n between 0 and mres
    # transfere data to g.rsgrid
    for i in range(0,len(g.rsgrid)):
            g.rsgrid[i].dens=g.rgrid[i+n*len(g.rsgrid)].dens
    model = []
    for v in g.rsgrid:
        m = Vector()
        m.xyz = v.xyz*v.dens*g.mres
        model.append(m)  
    global me
    global ob
    me = bpy.data.meshes.new("model")       # create a new mesh  
    ob = bpy.data.objects.new("model", me)  # create an object with that mesh
    g.scene.objects.link(ob)      # Link object to g.scene 
    # Fill the mesh with verts, edges, faces 
    me.from_pydata(model,[],g.sfaces)
    me.update()  
