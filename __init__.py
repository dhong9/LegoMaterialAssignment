# Builtin Modules
import bpy

bl_info = {
    "name": "Lego Material Assignment",
    "blender": (4, 2, 1),
    "location": "Properties editor",
    "author": "Daniel Hong",
    "description": "Assigns Lego material based on material name",
    "category": "3D View"
}

class LegoMaterialAssignmentOperator(bpy.types.Operator):
    """Lego Material Assignment Operator"""
    bl_idname = "mesh.assign_lego_material"
    bl_label = "Assign Lego Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.assign_lego_material(context)
        return {'FINISHED'}

    def assign_lego_material(self, context):
        
        colorMap = {
            "SOLID-LIME": 0xBBE90B,
            "SOLID-CORAL": 0xFF698F,
            "SOLID-BRIGHT_LIGHT_ORANGE": 0xF8BB3D,
            "SOLID-BRIGHT_LIGHT_YELLOW": 0xEBD800,
            "SOLID-BLACK": 0x051301,
            "SOLID-MEDIUM_AZURE": 0x36AEBF,
            "SOLID-LIGHT_BLUISH_GRAY": 0xAFB5C7
        }
        
        obj = context.active_object
        for idx, material in enumerate(obj.data.materials):
            matName, *_ = material.name.split('.')
            if matName in colorMap:
                print("Found material", material.name)
                
                hex_color = colorMap[matName]
                base_color = self.hex_to_rgb(hex_color)
                
                # Define principled shader
                material.use_nodes = True
                material.node_tree.nodes.clear()
                principled_bsdf = material.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
                principled_bsdf.inputs[0].default_value = base_color
                principled_bsdf.inputs[2].default_value = 0.2  # Roughness
                
                # Optionally add an output node and connect the shader
                output_node = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
                material.node_tree.links.new(principled_bsdf.outputs[0], output_node.inputs[0])
    
    def srgb_to_linearrgb(self, c):
        if c < 0:
            return 0
        if c < 0.04045:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4

    
    def hex_to_rgb(self, h, alpha=1):
        r = (h & 0xff0000) >> 16
        g = (h & 0x00ff00) >> 8
        b = (h & 0x0000ff)
        return tuple([self.srgb_to_linearrgb(c/0xff) for c in (r,g,b)] + [alpha])

def draw_mesh_context_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(LegoMaterialAssignmentOperator.bl_idname, text=LegoMaterialAssignmentOperator.bl_label)

def register():
    bpy.utils.register_class(LegoMaterialAssignmentOperator)
    
    # Register the context menu
    rcmenu = getattr(bpy.types, "VIEW3D_MT_object_context_menu", None)
    if rcmenu is None:
        rcmenu = bpy.types.VIEW3D_MT_object_context_menu
        bpy.utils.register_class(rcmenu)

    # Add draw function for the menu
    rcmenu.append(draw_mesh_context_menu)
    print("Registered Lego Material Assignment")

def unregister():
    # Unregister the operator and menu
    bpy.utils.unregister_class(LegoMaterialAssignmentOperator)
    rcmenu = bpy.types.VIEW3D_MT_object_context_menu
    rcmenu.remove(draw_mesh_context_menu)
    print("Unregistered Lego Material Assignment")

# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()