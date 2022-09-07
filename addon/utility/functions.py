import bpy
import os
import json

from .constants import *                   

def convert_ab_path(filepath):
    if filepath.startswith('//'):
            filepath = (os.path.abspath(bpy.path.abspath(filepath)) + '\\')

    return filepath


def json_check(json_path):

    try:
        with open(json_path) as json_file:
            json_data = json.load(json_file)
    except ValueError as e:
        print('QS: Invalid Json')
        return False
    return True


def set_principled_default():

    props = bpy.context.scene.principledtools
    
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


def set_base_color_default():

    props = bpy.context.scene.principledtools
    
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


def create_new_material(ob, material_name):

    # Creating Material
    new_material = bpy.data.materials.new(name=material_name)

    #Creating Slot
    slot_add = (len(bpy.data.objects[ob.name].material_slots))
    bpy.ops.object.material_slot_add()

    #Assigning material
    ob.data.materials[slot_add] = new_material
    bpy.ops.object.material_slot_assign()
    
    return new_material


def active_use_nodes(mat):

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

# Check Principled nodes if is necessary to use advanced color mode
def check_if_linked_base_color():

    props = bpy.context.scene.principledtools
    nodes = get_principled_nodes()

    for n in nodes:
        if n.inputs[0].links:
            return True 
    return False


def get_prefs():
    return bpy.context.preferences.addons[addon_name].preferences

# Get principled nodes from materials
def get_principled_nodes(create_materials = False):
    
    props = bpy.context.scene.principledtools
    prefs = get_prefs()
    
    # Create new material if not found any in selected objects
    def create_new_material_empty_data(obj, materials, nodes):
        if create_materials:
            if prefs.auto_new_material:
                
                mat = create_new_material(obj, "Material")               
                materials.append(mat)  
                
                if mat: 
                    props.principled_nodes_found += 1
                                      
    materials = [] # Store materials, in this way, principled nodes will not be duplicated
    nodes = []

    if props.enum_materials == 'ALL_MATERIALS':       
        objs = bpy.context.selected_objects

        for ob in objs:
            if hasattr(ob.data,'materials'):
                if ob.data.materials:                    
                    for mat in ob.data.materials:
                        if mat:
                            if not mat in materials:
                                if not mat.use_nodes:
                                    active_use_nodes(mat)

                                for nod in mat.node_tree.nodes:
                                    if nod.type == 'BSDF_PRINCIPLED':
                                        nodes.append(nod)
                                
                                materials.append(mat)
                else:
                    create_new_material_empty_data(ob, materials, nodes)                
    
    if props.enum_materials == 'ACTIVE_MATERIAL':        
        obj = bpy.context.active_object
   
        if obj:
            mat = obj.active_material
            if mat:
                if not mat.use_nodes:
                    active_use_nodes(mat)
                for nod in mat.node_tree.nodes:
                    if nod.type == 'BSDF_PRINCIPLED':
                        nodes.append(nod)
            else:
                create_new_material_empty_data(obj, materials, nodes)                
                   
    return nodes


def get_all_nodes(node_tree):
    
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
 
    
def create_mixing_color_group():
    
    #bpy.context.scene.use_nodes = True
    
    group_tree = bpy.data.node_groups.new(mix_color_group, 'ShaderNodeTree')
    
    group_in = group_tree.nodes.new('NodeGroupInput')

    group_tree.inputs.new('NodeSocketColor','New Value') #0
   
    group_out = group_tree.nodes.new('NodeGroupOutput')
    group_tree.outputs.new('NodeSocketColor','Output')
    
    # Mix Node
    
    mix_node = group_tree.nodes.new(type='ShaderNodeMixRGB')
    mix_node.name = mix_node_name
    mix_node.hide = True
    mix_node.inputs[0].default_value = 0
 
    # Hue Node

    hue_node = group_tree.nodes.new(type='ShaderNodeHueSaturation')
    hue_node.name = hue_node_name
    hue_node.hide = True
    hue_node.inputs[0].default_value = 0.5
    
    # B/C Node
    
    bc_node = group_tree.nodes.new(type='ShaderNodeBrightContrast')
    bc_node.name = bc_node_name
    bc_node.hide = True
    
    # Gamma
    
    gamma_node = group_tree.nodes.new(type='ShaderNodeGamma')
    gamma_node.name = gamma_node_name
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
   

def get_context_materials(context):
    '''Get all context materials, can be active material only or all materials in selected objects'''
    
    props = context.scene.principledtools
    materials = []
    
    if props.enum_materials == 'ALL_MATERIALS':       
        objs = context.selected_objects

        for ob in objs:
            if hasattr(ob.data,'materials'):
                if ob.data.materials:                    
                    for mat in ob.data.materials:
                        if mat:
                            if not mat in materials:
                                if not mat.use_nodes:
                                    active_use_nodes(mat)
                                materials.append(mat)
                #else:
                #    create_new_material_empty_data(ob, materials, nodes)                
    
    if props.enum_materials == 'ACTIVE_MATERIAL':        
        obj = context.active_object
   
        if obj:
            mat = obj.active_material
            if mat:
                if not mat.use_nodes:
                    active_use_nodes(mat)
                materials.append(mat)
                    
            #else:
            #    create_new_material_empty_data(obj, materials, nodes)  
    
    return materials
    

def get_node_from_color_mix_group(context, node_type):
    
    materials = get_context_materials(context)
    nodes = []
    
    for mat in materials:
        if not mat:
            continue
        
        if not mat.node_tree:
            continue
            
        for node in mat.node_tree.nodes:
            
            if not node.type == "GROUP":
                continue
        
            if not mix_color_group in node.name:
                continue
            
            if not node.node_tree:
                continue
            
            for n in node.node_tree.nodes:
                if n.type == node_type:
                    nodes.append(n)
    
    return nodes     
   
                                 
def reset_principled_node(node):
    
    node.inputs['Alpha'].default_value = 1
    node.inputs['Anisotropic'].default_value = 0
    node.inputs['Anisotropic Rotation'].default_value = 0
    #node.inputs['Base Color'].default_value = 1
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

# Function used to make all prop bool True, used when activating a preset
def reset_principled_node_preset():
    
    props = bpy.context.scene.principledtools
    
    for p in props.__annotations__:
        if p.startswith('use_') and not p.startswith('use_b') and not p.startswith('use_p'):
            if hasattr(props,p):
                setattr(props,p,True)
    
# -------------------------------------------------------------------
# Write and Load Data from JSON
# -------------------------------------------------------------------

def generate_smart_preset_data():
    #print("Loading Smart Preset Json")
    
    # Inner function to validates JSON values, checking if value exist, if not, replace by default (invalid)
    def get_key_value(data, key, invalid):
        if key in data:
            return data[key]
        else:
            return invalid
                  
    props = bpy.context.scene.principledtools
    
    if os.path.exists(smart_mat_s_path) and json_check(smart_mat_s_path): 
        
        with open(smart_mat_s_path, encoding='utf8') as json_file:
            
            data = json.load(json_file)  
            if not data["Smart Presets"]:
                empty_favorites = True
            else:
                
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
   
                    
def write_smart_mat_json(self,context):
        
    props = bpy.context.scene.principledtools
    
    if props.block_smart_material_setup_writing_data:
        return

    #print("Writing Smart Preset Data")
    
    data = {
        "Smart Presets" : {}
    }
    
    for i in props.smart_material_setup_presets:
        
        prop_detect = {}
        
        for pp in i.prop_data_detect:
            prop_detect[pp.prop_name] = [pp.prop_value,pp.prop_operation]
                    
        data["Smart Presets"][i.smart_preset_name] = {
            
            
            "preset": i.preset_to_activate,
            "active":i.active_preset,
            "select_node_setup": i.select_node_setup,
            
            "use_name_detect": i.use_name_detect,
            "name_detect_operation": i.name_detect_operation,
            "keys": i.material_string,
                       
            "use_rgb_detect": i.use_rgb_detect,
            "rgb_operation": i.rgb_operation,
            
            "detect_r":i.detect_r,
            "r_value":i.r_value,
            "r_operation":i.r_operation,
            
            "detect_g":i.detect_g,
            "g_value":i.g_value,
            "g_operation":i.g_operation,
            
            "detect_b":i.detect_b,
            "b_value":i.b_value,
            "b_operation":i.b_operation,
            
            "detect_a":i.detect_a,
            "a_value":i.a_value,
            "a_operation":i.a_operation,
            
            "use_prop_detect": i.use_prop_detect,
            "prop_detect_operation": i.prop_detect_operation,
            "prop_data_detect": prop_detect
                   
            }
                        
    with open(smart_mat_s_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def generate_preset_data():
        
    #print("Generating Preset Data")
    
    props = bpy.context.scene.principledtools
    
    if os.path.exists(favorites_path) and json_check(favorites_path): 
        
        with open(favorites_path, encoding='utf8') as json_file:
            
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
                        
                        if prop in vector3_prop:
                            new_prop.prop_value_vector3 = data["Presets"][i][prop]                  
                        else:
                            new_prop.prop_value = data["Presets"][i][prop]
   
                        
def write_preset_json(self,context):
    #print("Writing Preset Data")
        
    props = bpy.context.scene.principledtools
    
    data = {
        "Presets" : {}
    }
    
    for i in props.loaded_presets:
        prop_data = {}
        
        for p in i.preset_prop_data:
            if p.prop_name in vector3_prop:
                prop_data[p.prop_name] = [p.prop_value_vector3[0],p.prop_value_vector3[1],p.prop_value_vector3[2],p.prop_value_vector3[3]]                
            else:
                prop_data[p.prop_name] = p.prop_value
              
        data["Presets"][i.preset_name] = prop_data
                    
    with open(favorites_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



    
    
       
                           
                    
                    
                     
                    

            



    


        

    



