import bpy

def update_preset_enum_prop(self,context):
    '''Update enum prop (presets)'''
    
    Enum_items = [("NONE","None",""),]
    
    for preset in bpy.context.scene.principledtools.loaded_presets:
        
        data = preset.preset_name
        item = (data, data, data)
        
        Enum_items.append(item)
        
    return Enum_items