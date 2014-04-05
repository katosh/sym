import math
import bpy
from mathutils import Vector

### VERIFICATION ###

def show_reflection_planes(clusters=None, scene=bpy.context.scene):
    if len(clusters)==0: return
    print('the cluster densities are...')
    clusters.sort(key=lambda x: x.weight, reverse=True)
    maxdens = clusters[0].weight
    for cl in clusters:
        print(cl.weight,'at',cl.co)
        cl.draw(scene, maxdensity=maxdens)
