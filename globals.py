""" GLOBAL STUFF """

import bpy
import bmesh
bmesh.types.BMesh.free


### for geometry
bm=bmesh.new()  # THE GEOMETRY
scene = bpy.context.scene   # for visualisation

# geting an example geometry
bm.from_mesh(bpy.context.object.data)

### for sigature space
pc = 1.5	    # Pruning limit for curvature
#plimit = 0.0005	# limit of relative curvature difference for pairing
plimit = 0.1	# limit of relative curvature difference for pairing
sigs = []       # representation of signature space Omega
pruned = []     # Point sorted out by pruning
nsigs = 0       # length of signature list

### for transformation space
transfs = []    # transformation space
ntrans  = 0     # number of transformations
moff    = 0     # maximal reflection plane offset
mioff   = None  # minimal reflection plane offset
sfaces  = []    # hemisphere faces for visualization
ntransfs= 0     # number of transformations
diam    = 0     # object maximal diameter within unpruned points
# the diam is used for fisualisation of reflection planes in the verification step

### for clustering
mrad = 0.16	    # relative radius for mean shift (1 is the whole space)
mres = 50	    # resolution for Mean Shift
rgrid = []      # grid for reflection space
rsgrid = []     # grid for reflection space in just one offsetlayer
sfaces = []     # faces of hemisphere for visualization
maxima = None   # Maxima in mean shift surface
bref = None     # best reflection
