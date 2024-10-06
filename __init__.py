# Builtin Modules
import bpy
import csv
import os

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
        
        inputName = os.path.join(bpy.path.abspath("//"), "legoColors.csv")
        
        # Check if the file exists before trying to open it
        if not os.path.exists(inputName):
            self.report({'WARNING'}, f"File not found: {inputName}")
            print(f"File not found: {inputName}")
            return
        
        # Read input file into a dictionary
        with open(inputName, mode='r') as infile:
            reader = csv.reader(infile)
            colorMap = {rows[0]:rows[1] for rows in reader}
        
        obj = context.active_object
        for idx, material in enumerate(obj.data.materials):
            matName, *_ = material.name.split('.')
            if matName in colorMap:
                print("Found material", material.name)
                
                hex_color = colorMap[matName]
                base_color = self.hex_to_rgba(hex_color)
                
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

    def hex_to_rgba(self, hex_string):
        # Remove the '#' character if present
        hex_string = hex_string.lstrip('#')
        
        # Parse the hex string into RGB values
        if len(hex_string) == 6:  # Format: RRGGBB
            r = int(hex_string[0:2], 16)
            g = int(hex_string[2:4], 16)
            b = int(hex_string[4:6], 16)
            return tuple(self.srgb_to_linearrgb(c / 255.0) for c in (r, g, b)) + (1.0,)  # Default alpha to 1.0
        if len(hex_string) == 8:  # Format: RRGGBBAA
            r = int(hex_string[0:2], 16)
            g = int(hex_string[2:4], 16)
            b = int(hex_string[4:6], 16)
            a = int(hex_string[6:8], 16) / 255.0
            return tuple(self.srgb_to_linearrgb(c / 255.0) for c in (r, g, b)) + (a,)
        raise ValueError("Invalid hex format. Use #RRGGBB or #RRGGBBAA.")

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