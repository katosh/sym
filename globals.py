import bpy
import bmesh
bmesh.types.BMesh.free

""" GLOBAL VARIABLES """

### for geometry
bm=bmesh.new()  # THE GEOMETRY
scene = bpy.context.scene   # for visualisation

# geting an example geometry
bpy.ops.object.delete()	    # deleting the stupid cube
bpy.ops.mesh.primitive_monkey_add()
bpy.ops.object.delete()
bm.from_mesh(bpy.data.meshes["Suzanne"]) # get mesh data from model

### for sigature space
pc = 1.5	    # Pruning limit for curvature
plimit = 0.1	# limit of relative curvature difference for pairing
sigs = []       # representation of signature space Omega
pruned = []     # Point sorted out by pruning
laenge = 0      # length of signature list

### for transformation space
transfs = []    # transformation space
ntrans  = 0     # number of transformations
moff    = 0     # maximal reflection plane offset
sfaces  = []    # hemisphere faces for visualization

### for clustering
mrad = 0.08	    # relative radius for mean shift (1 is the whole space)
mres = 50	    # resolution for Mean Shift
rgrid = []      # grid for reflection space
rsgrid = []     # grid for reflection space in just one offsetlayer
sfaces = []     # faces of hemisphere for visualization
