#type: ignore 

import bpy

from bpy.types import PropertyGroup
                     

from ..utility.constants import *
from ..utility.functions import write_smart_mat_json
from .update_functions import *

# Collection of "PT_PresetsCollection.preset_prop_data" that holds each prop of a preset
class PT_PresetPropData(PropertyGroup):
    
    prop_name : bpy.props.StringProperty() 
    prop_value : bpy.props.FloatProperty()
    prop_value_vector3 : bpy.props.FloatVectorProperty(name='Base Color', size=4, subtype='COLOR', min=0, max=1,default=[1,1,1,1])

# Collection of "PT_Addon_Props.loaded_presets" that holds all presets
class PT_PresetsCollection(PropertyGroup):
    
    preset_name : bpy.props.StringProperty()  
    preset_prop_data : bpy.props.CollectionProperty(type=PT_PresetPropData)
       
class PT_SMSPropData(PropertyGroup):
    
    prop_name : bpy.props.StringProperty(update = write_smart_mat_json) 
    prop_value : bpy.props.FloatProperty(update = write_smart_mat_json)    
    prop_operation : bpy.props.EnumProperty(
        name= 'Operation',
        default = '==',
        update = write_smart_mat_json,
        items = [
            ('==','Equal', ''),
            ('<','Less Than', ''),
            ('>','More Than', ''),
        ]        
    )
      
class PT_SmartMaterialSetupPresets(PropertyGroup):
    # Class that holds all smart setups properties
    #
    # To add a new property, this new property should be:
    # - Registed in this class
    # - Added to write smart preset JSON Function "write_smart_mat_json"
    # - Added to load smart preset JSON Function "generate_smart_preset_data"
    # 
    # The name of the key in JSON and the name of the property in this class should be the same
    
    #toggle_edit : bpy.props.BoolProperty(name="Toggle Edit")
    
    active_preset: bpy.props.BoolProperty(default = True, name="Active Preset", update = write_smart_mat_json)    
    smart_preset_name : bpy.props.StringProperty(name="Smart Preset Name", update = write_smart_mat_json)
    preset_to_activate : bpy.props.EnumProperty(name= "Preset", items=update_preset_enum_prop, update = write_smart_mat_json)
    
    # Run Node Setup
    select_node_setup: bpy.props.EnumProperty(
        name= 'Select Node Setup',
        default = 'NONE',
        update = write_smart_mat_json,
        items = [
            ('NONE','None', ''),
            ('BUMP_SETUP','Bump Setup', ''),
            ('TRANSLUCENT_SETUP','Translucent Setup', ''),
        ]        
    )
    
    
    # Material Name Detect
    use_name_detect : bpy.props.BoolProperty(default = False, name='Use Name Detect', update = write_smart_mat_json)
    name_detect_operation: bpy.props.EnumProperty(
        name= 'Name Detect Operation',
        default = 'and',
        update = write_smart_mat_json,
        items = [
            ('and','And', ''),
            ('or','Or', ''),
        ]        
    )
    
    material_string : bpy.props.StringProperty(name="Name String", update = write_smart_mat_json) 
     
    # RGB detect
    
    use_rgb_detect: bpy.props.BoolProperty(default = False, name='Use RGB Detect', update = write_smart_mat_json)
    rgb_operation : bpy.props.EnumProperty(
        name= 'RGB Operation',
        default = 'and',
        update = write_smart_mat_json,
        items = [
            ('and','And', ''),
            ('or','Or', ''),
        ]        
    )
    
    detect_r: bpy.props.BoolProperty(default = False, name='Detect R', update = write_smart_mat_json)
    r_value : bpy.props.FloatProperty(update = write_smart_mat_json,name='R')
    r_operation : bpy.props.EnumProperty(
        name= 'Operation',
        default = '==',
        update = write_smart_mat_json,
        items = [
            ('==','Equal', ''),
            ('<','Less Than', ''),
            ('>','More Than', ''),
        ]        
    )
    
    detect_g: bpy.props.BoolProperty(default = False, name='Detect G', update = write_smart_mat_json)
    g_value : bpy.props.FloatProperty(update = write_smart_mat_json,name='G')
    g_operation : bpy.props.EnumProperty(
        name= 'Operation',
        default = '==',
        update = write_smart_mat_json,
        items = [
            ('==','Equal', ''),
            ('<','Less Than', ''),
            ('>','More Than', ''),
        ]        
    )
    
    detect_b: bpy.props.BoolProperty(default = False, name='Detect B', update = write_smart_mat_json)
    b_value : bpy.props.FloatProperty(update = write_smart_mat_json,name='B')
    b_operation : bpy.props.EnumProperty(
        name= 'Operation',
        default = '==',
        update = write_smart_mat_json,
        items = [
            ('==','Equal', ''),
            ('<','Less Than', ''),
            ('>','More Than', ''),
        ]        
    )
    
    detect_a: bpy.props.BoolProperty(default = False, name='Detect A', update = write_smart_mat_json)
    a_value : bpy.props.FloatProperty(update = write_smart_mat_json,name='A')
    a_operation : bpy.props.EnumProperty(
        name= 'Operation',
        default = '==',
        update = write_smart_mat_json,
        items = [
            ('==','Equal', ''),
            ('<','Less Than', ''),
            ('>','More Than', ''),
        ]        
    )
    
    # Prop Detect
    use_prop_detect : bpy.props.BoolProperty(default = False, name='Use Prop Detect', update = write_smart_mat_json)
    prop_detect_operation : bpy.props.EnumProperty(
        name= 'Prop Detect Operation',
        default = 'and',
        update = write_smart_mat_json,
        items = [
            ('and','And', ''),
            ('or','Or', ''),
        ]        
    )
    
    prop_data_detect : bpy.props.CollectionProperty(type=PT_SMSPropData)
    
    prop_to_add : bpy.props.EnumProperty(
        name= 'Add',
        default = 'Alpha',
        update = write_smart_mat_json,
        items = [
            ('Alpha','Alpha', ''),
            ('Roughness','Roughness', ''),
        ]        
    )
    
# Collection of "PT_Addon_Props.sms_ignore_materials" that holds all materials that were already changed in SMS
class PT_SmartMaterialSetupsIgnoreMaterials(PropertyGroup):
    
    material_data : bpy.props.PointerProperty(type= bpy.types.Material)
            
# Class that holds all properties of the add-on  
class PT_Addon_Props(PropertyGroup):
    
    auto_update : bpy.props.BoolProperty(default=True, name ='Auto Update')
    block_auto_update : bpy.props.BoolProperty(default=False, name ='Block Auto Update')

    enum_materials : bpy.props.EnumProperty(
        name= 'Material Data',
        default = '0',
        update = update_enum_materials_node_count,
        items = [
            ('0','All Materials', ''),
            ('1','Active Only', ''),
        ]        
    )
    
    # Temp Variables
    
    show_base_color_extras : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'}) 
    principled_nodes_found : bpy.props.IntProperty(default = 0 , options = {'SKIP_SAVE'}) 

    # Principled Props Bool

    use_base_color : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'}) # TODO Adicionar um update funtion pra não deixar mutado o mix node dos grupos de mixing
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
    use_b_use_color_mix : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'}) 
    use_b_color_mix_fac : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'})

    # HSV
    
    b_hue: bpy.props.FloatProperty(default=0.5, min=0, max=1, name='HUE', update=update_base_color_settings_closure('HUE'))
    b_saturation: bpy.props.FloatProperty(default=1, min=0, max=1, name='Saturation', update=update_base_color_settings_closure('SATURATION'))
    b_value: bpy.props.FloatProperty(default=1, min=0, max=1, name='Value', update=update_base_color_settings_closure('VALUE'))
    
    # B/C
    
    use_b_bright: bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'}) 
    use_b_contrast: bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'})
    
    b_bright: bpy.props.FloatProperty(default=1, min=-100, max=100, name='Bright', update=update_base_color_settings_closure('BRIGHT'))
    b_contrast: bpy.props.FloatProperty(default=1, min=-100, max=100, name='Contrast', update=update_base_color_settings_closure('CONTRAST'))
    
    # GAMMA
    
    use_b_gamma: bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'})
    
    b_gamma: bpy.props.FloatProperty(default=1, min=0, max=10, name='Gamma', update=update_base_color_settings_closure('GAMMA'))
    
    # Color Mix

    b_use_color_mix: bpy.props.BoolProperty(default=False,name='Use Color Mix', update=update_base_color_settings_closure('USE MIX'))
    b_color_mix_fac: bpy.props.FloatProperty(default=0.5, min=0, max=1, name='Mix Fac',update=update_base_color_settings_closure('MIX FAC'))
    
    # Preset System
    
    loaded_presets : bpy.props.CollectionProperty(type=PT_PresetsCollection)
    last_active_preset : bpy.props.StringProperty()
        
    # Smart Material System
    
    block_smart_material_setup_writing_data : bpy.props.BoolProperty(default=False) # Blocks writing update function to run in specific cases
    smart_material_setup_presets : bpy.props.CollectionProperty(type=PT_SmartMaterialSetupPresets) # Holds all smart presets
    sms_ignore_materials : bpy.props.CollectionProperty(type=PT_SmartMaterialSetupsIgnoreMaterials) # Holds material to be ignored whe running SMS
        
    sms_custom_index : bpy.props.IntProperty(default = 0)
    toggle_preset_edit : bpy.props.BoolProperty(default = False , options = {'SKIP_SAVE'})


    






