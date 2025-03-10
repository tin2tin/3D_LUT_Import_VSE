bl_info = {
    "name": "VSE LUT to Curve Modifier",
    "blender": (3, 0, 0),
    "category": "Sequencer",
    "description": "Import .cube LUT and apply RGB curves with optional desaturation via Hue Correction",
    "author": "tintwotin",
    "version": (1, 10),
    "location": "Sequencer > Add > Effects > LUT (Cube File)",
}

import bpy
import numpy as np

def load_cube_lut(file_path):
    """Load 3D LUT and extract diagonal samples"""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    lut_data = []
    size = None

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.upper().startswith('TITLE'):
            continue
        if line.startswith('LUT_3D_SIZE'):
            size = int(line.split()[-1])
            continue
        values = list(map(float, line.split()))
        if len(values) == 3:
            lut_data.append(values)

    if size is None or len(lut_data) != size ** 3:
        raise ValueError("Invalid .cube file format")

    lut_data = np.array(lut_data)
    diagonal_indices = [n + n * size + n * (size ** 2) for n in range(size)]
    return np.array([lut_data[i] for i in diagonal_indices]), size

def reduce_key_points(lut_data, max_points=256):
    """Reduce curve points while preserving key characteristics"""
    current_points = lut_data.shape[0]
    if current_points <= max_points:
        return lut_data.copy()

    x_old = np.linspace(0, 1, current_points)
    x_new = np.linspace(0, 1, max_points)

    return np.column_stack([
        np.interp(x_new, x_old, lut_data[:,0]),
        np.interp(x_new, x_old, lut_data[:,1]),
        np.interp(x_new, x_old, lut_data[:,2])
    ])

def convert_lut_to_curves(lut_data):
    """Convert LUT to RGB curve coordinates"""
    lut_data = reduce_key_points(lut_data)
    num_points = len(lut_data)
    x_values = np.linspace(0, 1, num_points)
    
    return [
        list(zip(x_values, lut_data[:,0])),
        list(zip(x_values, lut_data[:,1])),
        list(zip(x_values, lut_data[:,2]))
    ]

def apply_rgb_curves(strip, curve_r, curve_g, curve_b):
    """Apply/replace RGB curve modifier"""
    mod_name = "LUT RGB Curves"
    
    # Remove existing modifier
    for mod in list(strip.modifiers):
        if mod.type == 'CURVES' and mod.name == mod_name:
            strip.modifiers.remove(mod)
    
    # Create new modifier
    modifier = strip.modifiers.new(mod_name, 'CURVES')
    curves = modifier.curve_mapping
    curves.initialize()
    
    for (curve_data, chan_curve) in zip(
        [curve_r, curve_g, curve_b], curves.curves
    ):
        num_pt = len(curve_data)
        
        while len(chan_curve.points) < num_pt:
            chan_curve.points.new(0.0, 0.0)
        while len(chan_curve.points) > num_pt:
            chan_curve.points.remove(chan_curve.points[-1])
        
        for i, (x, y) in enumerate(curve_data):
            chan_curve.points[i].location = (x, y)
    
    curves.update()

def add_monochrome_mod(strip):
    """Add Hue Correction modifier to remove color"""
    mod_name = "Desaturation"
    
    # Remove duplicate monochrome modifiers
    for mod in list(strip.modifiers):
        if mod.type == 'HUE_CORRECT' and mod.name == mod_name:
            strip.modifiers.remove(mod)
    
    # Create new modifier
    hue_mod = strip.modifiers.new(mod_name, 'HUE_CORRECT')
    curves = hue_mod.curve_mapping
    curves.initialize()  # Ensure curves are initialized
    
    # Zero only the saturation curve (index 1)
    saturation_curve = curves.curves[1]
    for point in saturation_curve.points:
        point.location.y = 0.0  # Set saturation to 0
    
    # Leave hue (0) and value (2) curves untouched
    curves.update()

class SEQUENCER_OT_ImportCubeLUT(bpy.types.Operator):
    """Apply 3D LUT as RGB curves with optional desaturation via Hue Correction"""
    bl_idname = "sequencer.import_cube_lut"
    bl_label = "Import LUT & Desaturate (Cube File)"
    bl_options = {'REGISTER', 'UNDO'}

    monochrome: bpy.props.BoolProperty(
        name="Desaturate",
        description="Convert footage to grayscale using modified Hue Correction (saturation channels only)",
        default=False
    )

    filepath: bpy.props.StringProperty(
        subtype="FILE_PATH",
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "monochrome")

    def execute(self, context):
        try:
            lut_data, _ = load_cube_lut(self.filepath)
            curves = convert_lut_to_curves(lut_data)  # FIXED TYPO HERE
            curve_r, curve_g, curve_b = curves  # UNPACK CORRECTLY
            
            for strip in context.selected_sequences:
                if strip.type == 'SOUND':
                    continue
                apply_rgb_curves(strip, curve_r, curve_g, curve_b)
                
                if self.monochrome:
                    add_monochrome_mod(strip)
                    
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_add_lut(self, context):
    self.layout.operator(
        SEQUENCER_OT_ImportCubeLUT.bl_idname,
        text="LUT (Cube File)",
        icon='COLOR'
    )

def register():
    bpy.utils.register_class(SEQUENCER_OT_ImportCubeLUT)
    bpy.types.SEQUENCER_MT_add.append(menu_add_lut)

def unregister():
    bpy.utils.unregister_class(SEQUENCER_OT_ImportCubeLUT)
    bpy.types.SEQUENCER_MT_add.remove(menu_add_lut)

if __name__ == "__main__":
    register()
