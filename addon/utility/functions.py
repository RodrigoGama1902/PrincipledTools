import bpy
import os
import json

from .constants import *     

from bpy.types import Object, Material, Node, NodeGroup

def get_prefs():
    return bpy.context.preferences.addons[ADDON_NAME].preferences         

def convert_ab_path(filepath : str) -> str:
    '''Converts a relative path to an absolute path'''
    
    if filepath.startswith('//'):
            filepath = (os.path.abspath(bpy.path.abspath(filepath)) + '\\')

    return filepath


def json_check(json_path: str) -> bool:
    '''Simple check if the json file is valid'''

    try:
        with open(json_path) as json_file:
            json.load(json_file)
    except ValueError as e:
        print('QS: Invalid Json')
        return False
    return True


def set_principled_default(context) -> None:
    '''Reset the principled props to default values (visually only, that's why the block update is being used)'''

    props = context.scene.principledtools
    
    props.block_auto_update = True

    restore_auto = False
    if props.auto_update:
        props.auto_update = False
        restore_auto = True
        
    props.p_subsurface = 0
    props.p_subsurface_ior = 0
    props.p_subsurface_anisotropy = 0
    props.p_metallic = 0
    props.p_specular = 0.5
    props.p_specular_tint = 0
    props.p_roughness = 0.5
    props.p_anisotropic = 0
    props.p_anisotropic_rotation = 0
    props.p_sheen = 0
    props.p_sheen_tint = 0.5
    props.p_clearcoat = 0
    props.p_clearcoat_roughness = 0.03
    props.p_ior = 1.45
    props.p_transmission = 0
    props.p_transmission_roughness = 0
    props.p_emission_strength = 1
    props.p_alpha = 1
    props.p_normal = 1
    
    if restore_auto:
        props.auto_update = True
        
    props.block_auto_update = False


def set_base_color_default(context) -> None:
    '''Reset base color props to default values (visually only, that's why the block update is being used)'''

    props = context.scene.principledtools
    
    props.block_auto_update = True

    restore_auto = False
    if props.auto_update:
        props.auto_update = False
        restore_auto = True

    props.b_gamma = 1
    props.b_hue = 0.5
    props.b_bright = 0
    props.b_contrast = 0
    props.b_saturation = 1
    props.b_value = 1
    props.b_use_color_mix = True
    props.b_color_mix_fac = 0.5

    if restore_auto:
        props.auto_update = True
    
    props.block_auto_update = False


def create_new_material(ob : Object, material_name : str) -> Material:
    '''Creates a new material and assigns it to the object'''
    
    new_material = bpy.data.materials.new(name=material_name)
    slot_add = (len(bpy.data.objects[ob.name].material_slots))
    bpy.ops.object.material_slot_add()

    ob.data.materials[slot_add] = new_material
    bpy.ops.object.material_slot_assign()
    
    return new_material


def active_use_nodes_in_material(mat : Material) -> None:

    if not mat.node_tree:
        mat.use_nodes = True
        diffuse_color = mat.diffuse_color  
        created_nodes = [n for n in mat.node_tree.nodes]
        principled = [p for p in created_nodes if p.type == 'BSDF_PRINCIPLED']

        if principled:
            principled = principled[0]
            principled.inputs['Base Color'].default_value = diffuse_color   
    else:
        mat.use_nodes = True


def check_if_linked_base_color(context) -> bool:
    '''Check Principled nodes if is necessary to use advanced color mode'''

    nodes = get_context_principled_nodes(context)

    for n in nodes:
        if n.inputs[0].links:
            return True 
    return False


def get_context_materials(context, auto_create_materials = False) -> list[Material]:
    '''Get all context materials, can be active material only or all materials in selected objects'''
    
    props = context.scene.principledtools
    materials = []
        
    if props.enum_materials == 'ALL_MATERIALS':    
           
        for ob in context.selected_objects:
            if ob.data.materials:                    
                for mat in ob.data.materials:
                    if mat:
                        if not mat in materials:
                            if not mat.use_nodes:
                                active_use_nodes_in_material(mat)
                            materials.append(mat)
            else:
                if auto_create_materials:
                    materials.append(create_new_material(ob, "Material"))               
                    props.principled_nodes_found += 1 # This value updates automatically when the operator invokes,
                                                      # but since this function is called from the panel, it needs to be updated manually
                        
    if props.enum_materials == 'ACTIVE_MATERIAL':      
          
        ob = context.active_object
        if ob:
            mat = ob.active_material
            if mat:
                if not mat.use_nodes:
                    active_use_nodes_in_material(mat)
                materials.append(mat)              
            else:
                if auto_create_materials:
                    materials.append(create_new_material(ob, "Material"))               
                    props.principled_nodes_found += 1 
    
    return materials


def get_context_principled_nodes(context, auto_create_materials = False) -> list[Node]:
    '''Get principled nodes from context materials'''          
                                      
    materials = get_context_materials(context, auto_create_materials)
    nodes = []
    
    for mat in materials:
        for nod in mat.node_tree.nodes:
            if nod.type == 'BSDF_PRINCIPLED':
                nodes.append(nod)            
                   
    return nodes


def get_all_nodes(node_tree) -> list[Node]:
    '''Get all nodes from a node tree'''
    
    nodes = []
    
    for n in (node_tree.nodes if node_tree.type != 'GROUP' else node_tree.node_tree.nodes):
        if n.type == 'GROUP':
            nodes.append(n)
            group_nodes = get_all_nodes(n)
            
            for ng in group_nodes:               
                nodes.append(ng)
        else:
            nodes.append(n)
    
    return nodes
 
    
def create_mixing_color_group() -> NodeGroup:
    '''Creates a node group for mixing colors'''
        
    group_tree = bpy.data.node_groups.new(MIX_COLOR_GROUP_NAME, 'ShaderNodeTree')
    
    group_in = group_tree.nodes.new('NodeGroupInput')

    group_tree.inputs.new('NodeSocketColor','New Value') #0
   
    group_out = group_tree.nodes.new('NodeGroupOutput')
    group_tree.outputs.new('NodeSocketColor','Output')
    
    # Mix Node
    
    mix_node = group_tree.nodes.new(type='ShaderNodeMixRGB')
    mix_node.name = MIX_NODE_NAME
    mix_node.hide = True
    mix_node.inputs[0].default_value = 0.5
 
    # Hue Node

    hue_node = group_tree.nodes.new(type='ShaderNodeHueSaturation')
    hue_node.name = HUE_NODE_NAME
    hue_node.hide = True
    hue_node.inputs[0].default_value = 0.5
    
    # B/C Node
    
    bc_node = group_tree.nodes.new(type='ShaderNodeBrightContrast')
    bc_node.name = BC_NODE_NAME
    bc_node.hide = True
    
    # Gamma
    
    gamma_node = group_tree.nodes.new(type='ShaderNodeGamma')
    gamma_node.name = GAMMA_NODE_NAME
    gamma_node.hide = True

    # Locations
    
    mix_node.location = (0,0)
    hue_node.location = (mix_node.location[0] - 150, mix_node.location[1])
    bc_node.location = (hue_node.location[0] - 150, hue_node.location[1])
    gamma_node.location = (bc_node.location[0] - 150, bc_node.location[1])   
    
    group_in.location = (gamma_node.location[0] - 250,gamma_node.location[1])   
    group_out.location = (mix_node.location[0] + 250,mix_node.location[1])
      
    link = group_tree.links.new
    
    link(group_in.outputs[0], gamma_node.inputs[0])  
    link(gamma_node.outputs[0], bc_node.inputs[0]) 
    link(bc_node.outputs[0], hue_node.inputs[4])      
    link(hue_node.outputs[0], mix_node.inputs[1])
    link(mix_node.outputs[0], group_out.inputs[0])
    
    return group_tree  
         
                                 
def reset_principled_node(node) -> None:
    '''Reset the principled node main props to default values, used when activating a preset'''
    
    node.inputs['Alpha'].default_value = 1
    node.inputs['Anisotropic'].default_value = 0
    node.inputs['Anisotropic Rotation'].default_value = 0
    node.inputs['Clearcoat'].default_value = 0
    node.inputs['Clearcoat Roughness'].default_value = 0.03
    node.inputs['Emission Strength'].default_value = 1
    node.inputs['IOR'].default_value = 1.450
    node.inputs['Metallic'].default_value = 0
    node.inputs['Roughness'].default_value = 0.5
    node.inputs['Sheen'].default_value = 0
    node.inputs['Sheen Tint'].default_value = 0.5
    node.inputs['Specular'].default_value = 0.5
    node.inputs['Specular Tint'].default_value = 0
    node.inputs['Subsurface'].default_value = 0
    node.inputs['Subsurface IOR'].default_value = 0
    node.inputs['Subsurface Anisotropy'].default_value = 0
    node.inputs['Transmission'].default_value = 0
    node.inputs['Transmission Roughness'].default_value = 0


def reset_principled_node_preset(context):
    '''Function used to make all principled props bool values True, 
    since after executing the preset, all values will be updated, used when activating a preset'''
    
    props = context.scene.principledtools
    
    for p in props.__annotations__:
        if p.startswith('use_') and not p.startswith('use_b') and not p.startswith('use_p'):
            if hasattr(props,p):
                setattr(props,p,True)
    
# -------------------------------------------------------------------
# Write and Load Data from JSON
# -------------------------------------------------------------------

def generate_smart_preset_data(context) -> None:

    def get_key_value(data, key, invalid):
        '''Inner function to validates JSON values, checking if value exist, if not, replace by default (invalid)'''
        if key in data:
            return data[key]
        else:
            return invalid
                  
    props = context.scene.principledtools
    
    if not (os.path.exists(SMART_MATERIAL_PRESETS_PATH) and json_check(SMART_MATERIAL_PRESETS_PATH)):
        return None 
        
    with open(SMART_MATERIAL_PRESETS_PATH, encoding='utf8') as json_file:
        
        data = json.load(json_file)  
        if not data["Smart Presets"]:
            return None
            
        props.smart_material_setup_presets.clear()
        
        for i in data["Smart Presets"]: 
            
            props.block_smart_material_setup_writing_data = True
            
            try:                  
                preset_data = data["Smart Presets"][i]

                new_preset = props.smart_material_setup_presets.add()
                new_preset.smart_preset_name = i
                new_preset.active_preset = get_key_value(preset_data, "active", False)  
                
                new_preset.preset_to_activate = preset_data["preset"] if preset_data["preset"] in [p.preset_name for p in props.loaded_presets] else "NONE"
                
                new_preset.select_node_setup = get_key_value(preset_data, "select_node_setup", "NONE")
                
                # Name Detect
                
                new_preset.use_name_detect = get_key_value(preset_data, "use_name_detect", False)
                new_preset.name_detect_operation = get_key_value(preset_data, "name_detect_operation", "or")  
                new_preset.material_string = get_key_value(preset_data, "keys", " ")  
                
                # RBG Detect                                       
                new_preset.use_rgb_detect = get_key_value(preset_data, "use_rgb_detect", False)   
                new_preset.rgb_operation = get_key_value(preset_data, "rgb_operation", "or")    
                                
                new_preset.detect_r = get_key_value(preset_data, "detect_r", False)   
                new_preset.r_value = get_key_value(preset_data, "r_value", 0.0)    
                new_preset.r_operation = get_key_value(preset_data, "r_operation", "==") 
                
                new_preset.detect_g = get_key_value(preset_data, "detect_g", False)
                new_preset.g_value = get_key_value(preset_data, "g_value", 0.0) 
                new_preset.g_operation = get_key_value(preset_data, "g_operation", "==")
                
                new_preset.detect_b = get_key_value(preset_data, "detect_b", False)
                new_preset.b_value = get_key_value(preset_data, "b_value", 0.0) 
                new_preset.b_operation = get_key_value(preset_data, "b_operation", "==")
                
                new_preset.detect_a = get_key_value(preset_data, "detect_a", False)
                new_preset.a_value = get_key_value(preset_data, "a_value", 0.0) 
                new_preset.a_operation = get_key_value(preset_data, "a_operation", "==")
                                
                # Prop Detect
                new_preset.use_prop_detect = get_key_value(preset_data, "use_prop_detect", False)   
                new_preset.prop_detect_operation = get_key_value(preset_data, "prop_detect_operation", "or")  
                                        
                for pd in get_key_value(preset_data, "prop_data_detect", {}):
                    new_prop_detect = new_preset.prop_data_detect.add()
                    new_prop_detect.prop_name = pd
                    new_prop_detect.prop_value = preset_data["prop_data_detect"][pd][0]
                    new_prop_detect.prop_operation = preset_data["prop_data_detect"][pd][1] 
                        
            except:
                print("Loading Smart Preset Data Error")         
                
        props.block_smart_material_setup_writing_data = False       
   
                
def generate_preset_data():
        
    #print("Generating Preset Data")
    
    props = bpy.context.scene.principledtools
    
    if os.path.exists(FAVORITES_PATH) and json_check(FAVORITES_PATH): 
        
        with open(FAVORITES_PATH, encoding='utf8') as json_file:
            
            data = json.load(json_file)  
            if not data["Presets"]:
                empty_favorites = True
            else:
                
                props.loaded_presets.clear()
                
                for i in data["Presets"]: 

                    new_preset = props.loaded_presets.add()
                    new_preset.preset_name = i
                    
                    for prop in data["Presets"][i]:
                             
                        new_prop = new_preset.preset_prop_data.add()
                        new_prop.prop_name = prop
                        
                        if prop in VECTOR3_PROP:
                            new_prop.prop_value_vector3 = data["Presets"][i][prop]                  
                        else:
                            new_prop.prop_value = data["Presets"][i][prop]
   
                        
def write_preset_json(context):
    '''Write a new preset json'''

    props = context.scene.principledtools
    
    data = {
        "Presets" : {}
    }
    
    for i in props.loaded_presets:
        prop_data = {}
        
        for p in i.preset_prop_data:
            if p.prop_name in VECTOR3_PROP:
                prop_data[p.prop_name] = [p.prop_value_vector3[0],p.prop_value_vector3[1],p.prop_value_vector3[2],p.prop_value_vector3[3]]                
            else:
                prop_data[p.prop_name] = p.prop_value
              
        data["Presets"][i.preset_name] = prop_data
                    
    with open(FAVORITES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



    
    
       
                           
                    
                    
                     
                    

            



    


        

    



