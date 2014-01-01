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
    # even point grid on the sphere for clustering of reflection normal direction
    # https://perswww.kuleuven.be/~u0017946/publications/Papers97/art97a-Saff-Kuijlaars-MI/Saff-Kuijlaars-MathIntel97.pdf

    ### make hemisphere out of evenly spaced points
    Nu = 2*g.mres # resolution / number of directions to analyse weight
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
        g.rsgrid.append(v)
    # add normals perfectly parallel to axis because such cases ofte ocurr
    for i in range(1,4):
        v=svector()
        v.xyz = (i==1,i==2,i==3)
        g.rsgrid.append(v)


    ### show hemisphere in 3-d view and get faces of sphere-surface for later visualisation
    # detour over mesh to create bmesh from a list of vertecis
    global sphere
    global me
    me.from_pydata(g.rsgrid,[],[])              # Fill the mesh with verts, edges, faces 
    sphere.from_mesh(me)
    bmesh.ops.convex_hull(sphere,input=sphere.verts,use_existing_faces=False) # generate faces

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

### mean shift for reflectation space
maximum = svector()
def rmeanshift():
    # calculate density for each point of the grid
    global maximum
    g.ntrans = len(g.transfs)
    amw = g.mrad*math.pi		# angle mean width (search radius)
    omw = g.mrad*g.moff			# offset mean width (search radius)
    for v in g.rgrid:
        for t in g.transfs:
            # angle between the normals ignoring its sign
            diffa = math.pi - abs(math.pi - v.angle(t.rnor)) 
            # difference in reflectation offset
            diffo = abs(v.roff - t.roff)
            # linear weight looks like __/\__ 
            # where amw/omw is the maximal distance
            v.dens += max( 0 , (amw - diffa)/amw + (omw - diffo)/omw)
            # v.dens += max( 0 , (amw - diffa)/amw)   # ignoring offset
        v.dens = v.dens/g.ntrans  # normalization
        if v.dens > maximum.dens:
            maximum=v

### show offset layer with maximum
def showmrlayer():
    n = round((maximum.roff/g.moff)*g.mres)
    showrlayer(n)
    print('highest density at an offset of ',maximum.roff)
    print('this is level ',n,' of ',g.mres)
    print('the maximal offset is ',g.moff)
    print('the minimal offset is ',g.mioff)

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
