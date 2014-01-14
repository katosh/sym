import bpy
import sym
import tools

class UIPanel(bpy.types.Panel):
    bl_label = "Symmetry detection"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw (self, context):
        self.layout.operator("sym.reload")
        self.layout.operator("sym.debug")
        self.layout.operator("sym.show_cluster")

class show_cluster(bpy.types.Operator):
    bl_idname = "sym.show_cluster"
    bl_label = "show cluster"

    def execute(self, context):
        cls = sym.clusters
        tfs = sym.gamma

        cls.read_selection()
        select = []
        for cl in cls:
            if cls.get_vertex(cl).select == True:
                select.extend(cl.clusterverts)
        for tf in select:
            tfs.get_vertex(tf).select = True
        tfs.write_selection()

        bpy.context.scene.objects.active = tfs.obj
        bpy.ops.object.mode_set(mode='EDIT') # doesnt work
        return {'FINISHED'}

class debug(bpy.types.Operator):
    bl_idname = "sym.debug"
    bl_label = "debug"
    def execute(self, context): sym.debug(); return {'FINISHED'}

class reload(bpy.types.Operator):
    bl_idname = "sym.reload"
    bl_label = "reload"
    def execute(self, context): sym.reload(); return {'FINISHED'}

bpy.utils.register_module(__name__)
