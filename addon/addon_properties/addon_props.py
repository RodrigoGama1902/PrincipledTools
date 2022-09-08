#type: ignore 

import bpy

from bpy.types import PropertyGroup
                     
from ..utility.constants import *
from .update_functions import *
from .collection_props import *

def update_principled_props_closure(prop):
    '''closure to get property that trigged the main update function'''
        
    return lambda a,b: update_main_props(a,b,prop)

def update_base_color_settings_closure(prop):
    '''closure to get property that trigged the main update function'''
    
    return lambda a,b: update_color_props(a,b,prop)                

class PT_Addon_Props(PropertyGroup):
    '''Class that holds all properties of the add-on '''
    
    auto_update : bpy.props.BoolProperty(default=True, name ='Auto Update')
    block_auto_update : bpy.props.BoolProperty(default=False, name ='Block Auto Update')

    enum_materials : bpy.props.EnumProperty(
        name= 'Material Data',
        default = 'ALL_MATERIALS',
        update = update_enum_materials_node_count,
        items = [
            ('ALL_MATERIALS','All Materials', ''),
            ('ACTIVE_MATERIAL','Active Only', ''),
        ]        
    )
    
    # Temp Variables
    
    show_base_color_extras : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'}) 
    principled_nodes_found : bpy.props.IntProperty(default = 0 , options = {'SKIP_SAVE'}) 

    # Principled Props Bool

    use_base_color : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'})
    use_subsurface : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'}) 
    use_subsurface_ior : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'}) 
    use_subsurface_anisotropy : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'}) 
    use_metallic : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'}) 
    use_specular : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_specular_tint : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_anisotropic : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_anisotropic_rotation : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_roughness : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_sheen : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_sheen_tint : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_clearcoat : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_clearcoat_roughness : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_ior : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_emission_strength : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_alpha : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_transmission : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_transmission_roughness : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})
    use_normal : bpy.props.BoolProperty(default = False, options = {'SKIP_SAVE'})

    # Principled Props
    
    p_base_color: bpy.props.FloatVectorProperty(name='Base Color', size=4, subtype='COLOR', min=0, max=1,update=update_principled_props_closure('Base Color'),default=[1,1,1,1])
    p_subsurface: bpy.props.FloatProperty(default=0, min=0, max=1, name='Subsurface', update=update_principled_props_closure('Subsurface'))
    p_subsurface_ior: bpy.props.FloatProperty(default=0, min=1.010, max=3.800, name='Subsurface IOR', update=update_principled_props_closure('Subsurface IOR'))
    p_subsurface_anisotropy: bpy.props.FloatProperty(default=0, min=0, max=1, name='Subsurface Anisotropy', update=update_principled_props_closure('Subsurface Anisotropy'))
    p_metallic: bpy.props.FloatProperty(default=0, min=0, max=1, name='Metallic', update=update_principled_props_closure('Metallic'))
    p_specular: bpy.props.FloatProperty(default=0.5, min=0, max=1, name='Specular', update=update_principled_props_closure('Specular'))
    p_specular_tint: bpy.props.FloatProperty(default=0, min=0, max=1, name='Specular Tint', update=update_principled_props_closure('Specular Tint'))
    p_roughness: bpy.props.FloatProperty(default=0.5, min=0, max=1, name='Roughness', update=update_principled_props_closure('Roughness'))
    p_anisotropic: bpy.props.FloatProperty(default=0, min=0, max=1, name='Anisotropic', update=update_principled_props_closure('Anisotropic'))
    p_anisotropic_rotation: bpy.props.FloatProperty(default=0, min=0, max=1, name='Anisotropic Rotation', update=update_principled_props_closure('Anisotropic Rotation'))
    p_sheen: bpy.props.FloatProperty(default=0, min=0, max=1, name='Sheen', update=update_principled_props_closure('Sheen'))
    p_sheen_tint: bpy.props.FloatProperty(default=0, min=0, max=1, name='Sheen Tint', update=update_principled_props_closure('Sheen Tint'))
    p_clearcoat: bpy.props.FloatProperty(default=0, min=0, max=1, name='Clearcoat', update=update_principled_props_closure('Clearcoat'))
    p_clearcoat_roughness: bpy.props.FloatProperty(default=0, min=0, max=1, name='Clearcoat Roughness', update=update_principled_props_closure('Clearcoat Roughness'))
    p_ior: bpy.props.FloatProperty(default=1.45, min=0, max=100, precision=3,name='IOR', update=update_principled_props_closure('IOR'))
    p_transmission: bpy.props.FloatProperty(default=0, min=0, max=1, name='Transmission', update=update_principled_props_closure('Transmission'))
    p_transmission_roughness: bpy.props.FloatProperty(default=0, min=0, max=1, name='Transmission Roughness', update=update_principled_props_closure('Transmission Roughness'))
    p_emission_strength: bpy.props.FloatProperty(default=0, min=0, max=1, name='Emission Strength', update=update_principled_props_closure('Emission Strength'))
    p_alpha: bpy.props.FloatProperty(default=1, min=0, max=1, name='Alpha', update=update_principled_props_closure('Alpha'))
    p_normal: bpy.props.FloatProperty(default=1, min=0, max=100, name='Normal Strength', update=update_principled_props_closure('Normal'))

    # ----------------------------------------------------------------------------
    # Base color props
    # ----------------------------------------------------------------------------

    use_b_hue : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'}) 
    use_b_saturation : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'}) 
    use_b_value : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'}) 
    use_b_color_mix_fac : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'})

    # HSV
    
    b_hue: bpy.props.FloatProperty(default=0.5, min=0, max=1, name='Hue', update=update_base_color_settings_closure('Hue'))
    b_saturation: bpy.props.FloatProperty(default=1, min=0, max=1, name='Saturation', update=update_base_color_settings_closure('Saturation'))
    b_value: bpy.props.FloatProperty(default=1, min=0, max=1, name='Value', update=update_base_color_settings_closure('Value'))
    
    # B/C
    
    use_b_bright: bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'}) 
    use_b_contrast: bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'})
    
    b_bright: bpy.props.FloatProperty(default=1, min=-100, max=100, name='Bright', update=update_base_color_settings_closure('Bright'))
    b_contrast: bpy.props.FloatProperty(default=1, min=-100, max=100, name='Contrast', update=update_base_color_settings_closure('Contrast'))
    
    # GAMMA
    
    use_b_gamma: bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'})
    b_gamma: bpy.props.FloatProperty(default=1, min=0, max=10, name='Gamma', update=update_base_color_settings_closure('Gamma'))
    
    # Color Mix

    b_color_mix_fac: bpy.props.FloatProperty(default=0, min=0, max=1, name='Color Mix Fac',update=update_base_color_settings_closure('Color Mix Fac'))
    
    # Preset System
    
    loaded_presets : bpy.props.CollectionProperty(type=PT_PresetsCollection)
    last_active_preset : bpy.props.StringProperty()
        
    # Smart Material System
    
    block_smart_material_setup_writing_data : bpy.props.BoolProperty(default=False) # Blocks writing update function to run in specific cases
    smart_material_setup_presets : bpy.props.CollectionProperty(type=PT_SmartMaterialSetupPresets) # Holds all smart presets
    sms_ignore_materials : bpy.props.CollectionProperty(type=PT_SmartMaterialSetupsIgnoreMaterials) # Holds material to be ignored whe running SMS
        
    sms_custom_index : bpy.props.IntProperty(default = 0)
    toggle_preset_edit : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'})


    






