import bpy
import code
import sys
sys.path.append(r'.')   # add script path to system pathes to find the other modules
import globals as g

### Show the used mesh in 3-d view
def showmesh():
    mesh = bpy.data.meshes.new("Buttefly")
    g.bm.to_mesh(mesh)
    ob_new = bpy.data.objects.new("Butterfly", mesh)     
    g.scene.objects.link(ob_new)

showmesh()

import signatures as si
si.mksigs()

import transformations as tr
tr.mktransfs()  # make/fill transformation space
#tr.plotr()      # plotting the transformation space for refletions

import clustering as cl
cl.mkrgrid()        # make grid for reflectation space
#cl.showhemisphere()   # show one generatet hemisphere (one offset layer of the grid)
cl.rmeanshift()     # calculate the density of transformations for each grid point
#cl.showrlayer(0)    # show one offset layer with hight (or distance to (0,0,0)) representig density
cl.showmrlayer()     # show the offset layer where the density reaches its maximum

# code.interact(local=locals())   # interactive variable test

import verification as ver
ver.showplane()
