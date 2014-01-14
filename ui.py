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
        sel_cls = sym.clusters.get_selected()
        sel_tfs = [tf for cl in sel_cls for tf in cl.clusterverts]
        sym.gamma.set_selected(sel_tfs)
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
