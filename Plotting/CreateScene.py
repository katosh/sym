# quelle: http://www.gibert.biz/downloads/3dscatterplotswithblender
import bpy
import math
 
def removeObjects( scn ):
    for ob in scn.objects:
 
        if ob.type == 'MESH':
            scn.objects.unlink( ob )
 
def returnMaterialByName(passedName):
    result = None
    for m in bpy.data.materials:
        if m.name == passedName:
            result = m
            break
    return result

def createNewMaterial (passedName,passedcolor):
    tempMat = bpy.data.materials.new(passedName)
    if tempMat != None:
        tempMat.diffuse_color = passedcolor
        tempMat.diffuse_shader = 'LAMBERT'
        tempMat.diffuse_intensity = 1.0
        tempMat.specular_color = (0.9,0.9,0.9)
        tempMat.specular_shader = 'COOKTORR'
        tempMat.specular_intensity = 0.5
        tempMat.use_transparency=True
        tempMat.alpha = 0.5
        tempMat.ambient = 0.3
        tempMat.emit = 0.2
        #tempMat.diffuse_intensity=1
    return tempMat

def aquireOrCreateMaterial(passedName):
    tempMat = returnMaterialByName(passedName)
    if tempMat == None:
        tempMat = createNewMaterial(passedName)
    return tempMat

def newSph(diam):
    tempSph = bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, size=diam,location=(0, 0, 0), rotation=(0, 0, 0))
    return tempSph


# Program begins here.
scn = bpy.context.scene
removeObjects( scn )

k=1
xmin=200000
ymin=200000
zmin=200000
xmax=-200000
ymax=-200000
zmax=-200000
#rawfile=open("/Users/mgibert/Boulot/BlenderStuff/test.txt","r")
#rawfile=open("/Users/mgibert/Boulot/BlenderStuff/test_vel.txt","r")
rawfile=open("/Users/mgibert/Boulot/HVK/101004/smallpart_out_bigpart.txt","r")
tabraw=rawfile.readlines()
rawfile.close()
for ligne in tabraw:
    ligne=ligne.replace('\n','')
    l=ligne.split(',')

    print(ligne)
    x=float(l[0])*100
    y=float(l[1])*100
    z=float(l[2])*100
    #print(l[6])
    r=float(l[6])
    g=float(l[7])
    b=float(l[8])
    n=float(l[9])
    #n=.01
    xmin=min(xmin,x)
    ymin=min(ymin,y)
    zmin=min(zmin,z)
    xmax=max(xmax,x)
    ymax=max(ymax,y)
    zmax=max(zmax,z)

    newSph(n)
    ob = bpy.context.active_object
    ob.name = "part"
    ob.location=(x,y,z)
    me = ob.data
    color=(r,g,b)
    #mat = aquireOrCreateMaterial("myNewMaterial5")
    mat = createNewMaterial("myNewMaterial",color)
    me.materials.append(mat)

    k=k+1

r=0.2
g=0.2
b=0.2
sc=10
bpy.ops.mesh.primitive_plane_add(location=(xmin,ymin,zmin))
ob = bpy.context.active_object
ob.name = "plan"
ob.scale=(sc,sc,sc)
me = ob.data
color=(r,g,b)
mat = createNewMaterial("myNewMaterial",color)
me.materials.append(mat)

bpy.ops.mesh.primitive_plane_add(location=(xmin,ymax,zmax),rotation=(0,3.14/2,0))
ob = bpy.context.active_object
ob.name = "plan"
ob.scale=(sc,sc,sc)
me = ob.data
color=(r,g,b)
mat = createNewMaterial("myNewMaterial",color)
me.materials.append(mat)

bpy.ops.mesh.primitive_plane_add(location=(xmax,ymax,zmax),rotation=(0,3.14/2,3.14/2))
ob = bpy.context.active_object
ob.name = "plan"
ob.scale=(sc,sc,sc)
me = ob.data
color=(r,g,b)
mat = createNewMaterial("myNewMaterial",color)
me.materials.append(mat)
