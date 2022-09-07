#type:ignore

import bpy

from bpy.types import PropertyGroup

from .update_functions import *
from .enum_functions import *

class PT_PresetPropData(PropertyGroup):
    '''Collection of "PT_PresetsCollection.preset_prop_data" that holds each prop of a preset'''
    
    prop_name : bpy.props.StringProperty() 
    prop_value : bpy.props.FloatProperty()
    prop_value_vector3 : bpy.props.FloatVectorProperty(name='Base Color', size=4, subtype='COLOR', min=0, max=1,default=[1,1,1,1])


class PT_PresetsCollection(PropertyGroup):
    '''Collection of "PT_Addon_Props.loaded_presets" that holds all presets'''
    
    preset_name : bpy.props.StringProperty()  
    preset_prop_data : bpy.props.CollectionProperty(type=PT_PresetPropData)
       
class PT_SMSPropData(PropertyGroup):
    
    prop_name : bpy.props.StringProperty(update = write_update_smart_mat_json) 
    prop_value : bpy.props.FloatProperty(update = write_update_smart_mat_json)    
    prop_operation : bpy.props.EnumProperty(
        name= 'Operation',
        default = '==',
        update = write_update_smart_mat_json,
        items = [
            ('==','Equal', ''),
            ('<','Less Than', ''),
            ('>','More Than', ''),
        ]        
    )

class PT_SmartMaterialSetupPresets(PropertyGroup):
    '''
    Class that holds all smart setups properties
    
    To add a new property, this new property should be:
    - Registered in this class
    - Added to write smart preset JSON Function "write_update_smart_mat_json"
    - Added to load smart preset JSON Function "generate_smart_preset_data"
     
    The name of the key in JSON and the name of the property in this class should be the same
    
    #toggle_edit : bpy.props.BoolProperty(name="Toggle Edit")'''
    
    active_preset: bpy.props.BoolProperty(default = True, name="Active Preset", update = write_update_smart_mat_json)    
    smart_preset_name : bpy.props.StringProperty(name="Smart Preset Name", update = write_update_smart_mat_json)
    preset_to_activate : bpy.props.EnumProperty(name= "Preset", items=get_presets_enum_items, update = write_update_smart_mat_json)
    
    # Run Node Setup
    select_node_setup: bpy.props.EnumProperty(
        name= 'Select Node Setup',
        default = 'NONE',
        update = write_update_smart_mat_json,
        items = [
            ('NONE','None', ''),
            ('BUMP_SETUP','Bump Setup', ''),
            ('TRANSLUCENT_SETUP','Translucent Setup', ''),
        ]        
    )
    
    
    # Material Name Detect
    use_name_detect : bpy.props.BoolProperty(default = False, name='Use Name Detect', update = write_update_smart_mat_json)
    name_detect_operation: bpy.props.EnumProperty(
        name= 'Name Detect Operation',
        default = 'and',
        update = write_update_smart_mat_json,
        items = [
            ('and','And', ''),
            ('or','Or', ''),
        ]        
    )
    
    material_string : bpy.props.StringProperty(name="Name String", update = write_update_smart_mat_json) 
     
    # RGB detect
    
    use_rgb_detect: bpy.props.BoolProperty(default = False, name='Use RGB Detect', update = write_update_smart_mat_json)
    rgb_operation : bpy.props.EnumProperty(
        name= 'RGB Operation',
        default = 'and',
        update = write_update_smart_mat_json,
        items = [
            ('and','And', ''),
            ('or','Or', ''),
        ]        
    )
    
    detect_r: bpy.props.BoolProperty(default = False, name='Detect R', update = write_update_smart_mat_json)
    r_value : bpy.props.FloatProperty(update = write_update_smart_mat_json,name='R')
    r_operation : bpy.props.EnumProperty(
        name= 'Operation',
        default = '==',
        update = write_update_smart_mat_json,
        items = [
            ('==','Equal', ''),
            ('<','Less Than', ''),
            ('>','More Than', ''),
        ]        
    )
    
    detect_g: bpy.props.BoolProperty(default = False, name='Detect G', update = write_update_smart_mat_json)
    g_value : bpy.props.FloatProperty(update = write_update_smart_mat_json,name='G')
    g_operation : bpy.props.EnumProperty(
        name= 'Operation',
        default = '==',
        update = write_update_smart_mat_json,
        items = [
            ('==','Equal', ''),
            ('<','Less Than', ''),
            ('>','More Than', ''),
        ]        
    )
    
    detect_b: bpy.props.BoolProperty(default = False, name='Detect B', update = write_update_smart_mat_json)
    b_value : bpy.props.FloatProperty(update = write_update_smart_mat_json,name='B')
    b_operation : bpy.props.EnumProperty(
        name= 'Operation',
        default = '==',
        update = write_update_smart_mat_json,
        items = [
            ('==','Equal', ''),
            ('<','Less Than', ''),
            ('>','More Than', ''),
        ]        
    )
    
    detect_a: bpy.props.BoolProperty(default = False, name='Detect A', update = write_update_smart_mat_json)
    a_value : bpy.props.FloatProperty(update = write_update_smart_mat_json,name='A')
    a_operation : bpy.props.EnumProperty(
        name= 'Operation',
        default = '==',
        update = write_update_smart_mat_json,
        items = [
            ('==','Equal', ''),
            ('<','Less Than', ''),
            ('>','More Than', ''),
        ]        
    )
    
    # Prop Detect
    use_prop_detect : bpy.props.BoolProperty(default = False, name='Use Prop Detect', update = write_update_smart_mat_json)
    prop_detect_operation : bpy.props.EnumProperty(
        name= 'Prop Detect Operation',
        default = 'and',
        update = write_update_smart_mat_json,
        items = [
            ('and','And', ''),
            ('or','Or', ''),
        ]        
    )
    
    prop_data_detect : bpy.props.CollectionProperty(type=PT_SMSPropData)
    
    prop_to_add : bpy.props.EnumProperty(
        name= 'Add',
        default = 'Alpha',
        update = write_update_smart_mat_json,
        items = [
            ('Alpha','Alpha', ''),
            ('Roughness','Roughness', ''),
        ]        
    )

class PT_SmartMaterialSetupsIgnoreMaterials(PropertyGroup):
    '''Collection of "PT_Addon_Props.sms_ignore_materials" that holds all materials that were already changed in SMS'''
    
    material_data : bpy.props.PointerProperty(type= bpy.types.Material)