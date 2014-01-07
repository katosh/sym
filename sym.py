import bpy
import code
import sys
sys.path.append(r'.')   # add script path to system pathes to find the other modules
import globals as g
import bmesh

def run(obj=None):
    g.bm=bmesh.new()
    if type(obj)==bpy.types.Object:
        g.bm.from_mesh(obj.data)
    else:
        g.bm.from_mesh(bpy.context.object.data)

    print('calculating signatures...')
    import signatures as si
    si.mksigs()

    print('filling the transformation space...')
    import transformations as tr
    g.transfs = tr.Transformations(g.sigs) # compute transformation space
    g.transfs.plot(g.scene) # plotting the transformation space for refletions
    print('found',len(g.transfs),'transformations')

    import meanshift
    g.clusters=meanshift.cluster(g.transfs)
    #g.clusters.plot(g.scene)
    meanshift.plot_clusters(g.clusters)

#   print('clustering...')
#   import clustering as cl
#   cl.mkrgrid()        # make grid for reflectation space
    #cl.showhemisphere()   # show one generatet hemisphere (one offset layer of the grid)
#   cl.rmeanshift()     # calculate the density of transformations for each grid point
    #cl.showrlayer(0)    # show one offset layer with hight (or distance to (0,0,0)) representig density
    #cl.showmrlayer()     # show the offset layer where the density reaches its maximum
#   cl.showdata() # show some written data

    # code.interact(local=locals())   # interactive variable test

#   print('verifying symmetries...')
#   import verification as ver
#   ver.showplane()

def createsuzanne():
    import bmesh
    bm=bmesh.new()
    bpy.ops.object.delete()            # deleting the stupid cube
    bpy.ops.mesh.primitive_monkey_add()
    bpy.ops.object.delete()
    bm.from_mesh(bpy.data.meshes["Suzanne"]) # get mesh data from model
    mesh = bpy.data.meshes.new("Apemesh")
    bm.to_mesh(mesh)
    ob_new = bpy.data.objects.new("Apeobj", mesh)
    g.scene.objects.link(ob_new)
    return ob_new


if __name__ == "__main__":
    run(createsuzanne())