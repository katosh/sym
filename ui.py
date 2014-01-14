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
        self.layout.operator("sym.cls_to_tfs")

class cls_to_tfs(bpy.types.Operator):
    bl_idname = "sym.cls_to_tfs"
    bl_label = "selected cls to tfs"
    def execute(self, context):
        sel_cls = sym.clusters.get_selected()
        sel_tfs = [tf for cl in sel_cls for tf in cl.clusterverts]
        sym.tfS.set_selected(sel_tfs)
        return {'FINISHED'}
        
class tfs_to_sigs:
    bl_idname = "sym.tfs_to_sigs"
    bl_label = "selected tfs to sigs"    
    def execute(self, context):
        sel_tfs = sym.tfS.get_selected()
        #sel_sigs = [tf. for tf in sel_tfs]

class debug(bpy.types.Operator):
    bl_idname = "sym.debug"
    bl_label = "debug"
    def execute(self, context): sym.debug(); return {'FINISHED'}

class reload(bpy.types.Operator):
    bl_idname = "sym.reload"
    bl_label = "reload"
    def execute(self, context): sym.reload(); return {'FINISHED'}

bpy.utils.register_module(__name__)
