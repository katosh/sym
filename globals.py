import bpy
import bmesh
bmesh.types.BMesh.free

### global variables

bm=bmesh.new()  # THE GEOMETRY
scene = bpy.context.scene   # for visualisation

# geting an example geometry
bpy.ops.object.delete()	    # deleting the stupid cube
bpy.ops.mesh.primitive_monkey_add()
bpy.ops.object.delete()
bm.from_mesh(bpy.data.meshes["Suzanne"]) # get mesh data from model


pc = 1.5	    # Pruning limit for curvature
plimit = 0.1	# limit of relative curvature difference for pairing
mrad = 0.08	    # relative radius for mean shift (1 is the whole space)
mres = 50	    # resolution for Mean Shift


sigs = []       # representation of signature space Omega
pruned = []     # Point sorted out by pruning
laenge = 0      # length of signature list

transfs = []    # transformation space
ntrans  = 0     # number of transformations
moff    = 0     # maximal reflection plane offset
