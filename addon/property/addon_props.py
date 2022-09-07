import bpy
import json

from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)

from ..utility.constants import *
from ..utility.functions import (active_use_nodes,
                                 get_principled_nodes,
                                 check_if_linked_base_color,
                                 create_mixing_color_group,
                                 set_principled_default,
                                 json_check,
                                 write_smart_mat_json,
                                 reset_principled_node,
                                 reset_principled_node_preset)

# Update enum prop (presets)
def update_preset_enum_prop(self,context):
    
    Enum_items = [("NONE","None",""),]
    
    for preset in bpy.context.scene.principledtools.loaded_presets:
        
        data = preset.preset_name
        item = (data, data, data)
        
        Enum_items.append(item)
        
    return Enum_items
    
# Use to active selected preset 
def activate_selected_preset(self, context, preset_name, principled = None, load_mode = 'UPDATE_PROP'):
        
    empty_favorites = False
    
    set_principled_default()
    reset_principled_node_preset()
    
    if principled:
        reset_principled_node(principled)

    props = bpy.context.scene.principledtools
    
    for i in props.loaded_presets:                    
        if i.preset_name == preset_name:
            for p in i.preset_prop_data:
                
                if load_mode == 'UPDATE_PROP':

                    prop_name = p.prop_name.lower()
                    prop_name = prop_name.replace(' ','_')
                    prop_p = 'p_' + prop_name
                    prop_use = 'use_' + prop_name
                    
                    if p.prop_name in vector3_prop:
                        setattr(props,prop_p,p.prop_value_vector3)                  
                    else:
                        setattr(props,prop_p,p.prop_value)
                                  
                    setattr(props,prop_use,True)

                    if props.auto_update:
                        update_props(self,context,'All')
                
                if load_mode == 'DIRECT':                        
                    if principled:

                        if p:               
                            input = principled.inputs.get(p.prop_name)                            
                            if input:
                                if p.prop_name in vector3_prop:
                                    input.default_value = p.prop_value_vector3               
                                else:
                                    input.default_value = p.prop_value
                                
# Create Help Color Group on input base color when necessary
def base_color_helper(node_tree, input,value,principled):
    
    props = bpy.context.scene.principledtools

    default_x_offset = principled.location[0] -150

    y_input_locations = {
        'Base Color': (default_x_offset, principled.location[1] - 105),     
    }
    
    # TODO adicionar verificação se os principled selecionados tem input de base color
    # Se tiver, e esse aqui não, criar um input RGB node, pra poder sofrer os ajustes de HSV corretamente
    
    mix_group = None
    
    if input.links: 
        if not input.links[0].from_node.name.startswith(mix_color_group):
            
            new_mix_group = create_mixing_color_group()
            
            mix_group = node_tree.nodes.new('ShaderNodeGroup')
            mix_group.node_tree = bpy.data.node_groups[new_mix_group.name]
            mix_group.name = mix_color_group
            mix_group.location = y_input_locations['Base Color']
            mix_group.hide = True
            
            link = node_tree.links.new
    
            link(mix_group.inputs[0], input.links[0].from_socket)
            link(mix_group.outputs[0], input)     
             
        else:
            mix_group = input.links[0].from_node
                       
        props.use_b_use_color_mix = True     
        
        mix_node = [n for n in mix_group.node_tree.nodes if n.type == 'MIX_RGB']
        if mix_node:
            mix_node = mix_node[0]            
            mix_node.inputs[2].default_value = value 

    else:
        if value:
            input.default_value = value
            
    return mix_group

# Creates Math and Clamp nodes when current input has any node connected in
def math_node_helper(node_tree, input,value,principled):
    
    # Generate correct y position using y-index from node input
    def constant_y_position(y_index, base_y = 189):
        
        y = base_y + (22.1 * y_index)
        
        return principled.location[1] - y

    default_x_offset = principled.location[0] -150

    y_input_locations = {
        'Subsurface': (default_x_offset, principled.location[1] - 125),
        'Subsurface IOR': (default_x_offset, constant_y_position(0)),
        'Subsurface Anisotropy': (default_x_offset, constant_y_position(1)),
        'Metallic': (default_x_offset, constant_y_position(2)),
        'Specular': (default_x_offset, constant_y_position(3)),
        'Specular Tint': (default_x_offset, constant_y_position(4)),
        'Roughness': (default_x_offset, constant_y_position(5)),
        'Anisotropic': (default_x_offset, constant_y_position(6)),
        'Anisotropic Rotation': (default_x_offset, constant_y_position(7)),
        'Sheen': (default_x_offset, constant_y_position(8)),
        'Sheen Tint': (default_x_offset, constant_y_position(9)),
        'Clearcoat': (default_x_offset, constant_y_position(10)),
        'Clearcoat Roughness': (default_x_offset, constant_y_position(11)),
        'IOR': (default_x_offset, constant_y_position(12)),
        'Transmission': (default_x_offset, constant_y_position(13)),
        'Transmission Roughness': (default_x_offset, constant_y_position(14)),
        'Emission Strength': (default_x_offset, constant_y_position(16)),
        'Alpha': (default_x_offset, constant_y_position(17)),
    }

    if input.links: 
       
        if not input.links[0].from_node.name.startswith(multiply_node_name):

            math_node = node_tree.nodes.new(type='ShaderNodeMath')
            math_node.name = multiply_node_name
            math_node.hide = True
            math_node.operation = 'MULTIPLY'
            math_node.use_clamp = True
            math_node.location = y_input_locations[input.name]
            
            link = node_tree.links.new
            link(math_node.inputs[0], input.links[0].from_socket)
            link(math_node.outputs[0], input)

        else:
            math_node = input.links[0].from_node
        
        math_node.inputs[1].default_value = value * 2
    else:
        input.default_value = value

# -------------------------------------------------------------
# Update Props Settings
# Update Principled Props Real Time
# -------------------------------------------------------------

# closure to get property that trigged the main update function
def update_principled_props_closure(prop):
        
    return lambda a,b: update_props(a,b,prop)

# Update normal input prop (Only used when principled prop name is 'Normal')
def update_normal_principled_input(self, input, origin, node_tree, principled):

    # Function used to find and modify bump or normal map node
    def update_found_normal_node(from_node, from_socket):
        # This is function is recursion ready, meaning the sometimes will get group node and normal/bump nodes

        # If the node is bump/normal, this function will skip the process of find normal/bump nodes inside group
        # if the node is group type, will run this task below to find bump/normal nodes

        if from_node.type == 'GROUP':

            node_tree = from_node.node_tree

            # this function is recursion ready, and it will find the next node, even if the node is linked if unlimited reroutes node
            def ignore_reroute_node(node):

                if node.inputs[0].links:
                    if not node.inputs[0].links[0].from_node.type == 'REROUTE':
                        return node.inputs[0].links[0].from_node, node.inputs[0].links[0].from_socket
                    else:
                        return ignore_reroute_node(node)
                else:
                    return None
                
            # get output node inside group
            g_output = [n for n in from_node.node_tree.nodes if n.type == 'GROUP_OUTPUT']

            if g_output:
                g_output = g_output[0]

            # get input socket of output node

            # This process is necessary to get what socket is connected to the group output socket called 'Normal' (Or any other name)

            input_socket = None

            for i in g_output.inputs:

                if i.name == from_socket.name:
                    input_socket = i 
                    break
        
            # Get socket and node if this next node found inside this group (can be another group, or another node)
            # if the next node inside this group is a reroute node, it will run the ignore reroute node function, and this function will return the next node

            from_socket_node = None
            from_socket_socket = None
        
            if input_socket:
                if input_socket.links:

                    from_socket_node = input_socket.links[0].from_node

                    if from_socket_node.type == 'REROUTE':
                        from_socket_node, from_socket_socket = ignore_reroute_node(from_socket_node)
                    else:
                        from_socket_socket = input_socket.links[0].from_socket

        else:

            # if te input node is not a group, these values will be update for that in the next step, the variables will work with the input node was a bump/Normal node, or group node
            
            from_socket_node = from_node
            node_tree = from_socket_node.id_data

        if from_socket_node:

            # if this node is a group, all this process will be repeated with recursion, if not, the bump/normal map nodes will have it strength value corrected
                        
            if from_socket_node.type == 'BUMP' or from_socket_node.type == 'NORMAL_MAP':
                
                if from_socket_node.inputs[0].links:
                    if not from_socket_node.inputs[0].links[0].from_node.name.startswith(multiply_node_name):

                        math_node = node_tree.nodes.new(type='ShaderNodeMath')
                        math_node.name = multiply_node_name
                        math_node.hide = True
                        math_node.operation = 'MULTIPLY'

                        if from_socket_node.parent:
                            math_node.parent = from_socket_node.parent

                        math_node.location = from_socket_node.location[0] - 150, from_socket_node.location[1] - 100
                        
                        link = node_tree.links.new
                        link(math_node.inputs[0], from_socket_node.inputs[0].links[0].from_socket)
                        link(math_node.outputs[0], from_socket_node.inputs[0])
                    
                    else:
                        math_node = from_socket_node.inputs[0].links[0].from_node

                    math_node.inputs[1].default_value = props.p_normal
                    props.use_normal = True
                
                else:
                    from_socket_node.inputs[0].default_value = props.p_normal
                    props.use_normal = True
            
            if from_socket_node.type == 'GROUP':
                update_found_normal_node(from_socket_node, from_socket_socket)
    
    i = input
    n = principled 

    props = bpy.context.scene.principledtools

    if i.name == origin: # if True, means that this property is changing real time, so the prop bool should be set to True
        setattr(props,'use_normal', True)
    
    if not principled.inputs['Normal'].links: # this function will not run if the found principled does not have normal input
        return
    
    if props.auto_update or origin == 'All': # lock to only run this function if it was trigged by operator or auto update
        if props.use_normal:
        
            from_node = principled.inputs['Normal'].links[0].from_node
            from_socket = principled.inputs['Normal'].links[0].from_socket

            # this function will get node and socket connected to principled normal input
            update_found_normal_node(from_node, from_socket)

# This function will automatically update each principled prop by it input name
def update_single_principled_prop(self, input, origin, node_tree, principled, prop_name):

    i = input
    n = principled 

    props = bpy.context.scene.principledtools

    prop_name = prop_name.replace(' ','_') # Replace empty spaces like in "Transmission Roughness"

    prop = getattr(props,'p_' + prop_name)
    prop_bool = getattr(props,'use_' + prop_name)

    if i.name == origin: # if True, means that this property is changing real time, so the prop bool should be set to True
        setattr(props,'use_' + prop_name, True)

    if props.auto_update or origin == 'All': # If True, means that the update_props function is running through operator or through auto update                
        if prop_bool:
            if prop_name == 'base_color':   # Base color update is different than simple props updates that will use math node helpers 
                base_color_helper(node_tree, i, prop,n)
            else:
                math_node_helper(node_tree, i, prop,n)
        
# Main Update Props Function       
def update_props(self,context,origin):
    
    if hasattr(self,'block_auto_update'):
        if self.block_auto_update:
            return

    nodes = get_principled_nodes(create_materials = True)
    
    for n in nodes:
        node_tree = n.id_data 

        for i in n.inputs:            
            if i.name == origin or origin == 'All': #Check to update only changing property

                simple_update = ['Base Color','Subsurface','Subsurface IOR','Subsurface Anisotropy','Metallic','Specular','Specular Tint','Roughness','Anisotropic','Anisotropic Rotation','Sheen','Sheen Tint','Clearcoat','Clearcoat Roughness','IOR','Transmission','Transmission Roughness','Emission Strength','Alpha']

                if i.name in simple_update:
                                  
                    update_single_principled_prop(self, i, origin, node_tree, n, i.name.lower())
                
                if i.name == 'Normal':

                    update_normal_principled_input(self, i, origin, node_tree, n)
                    
# -------------------------------------------------------------
# Base Color Settings
# -------------------------------------------------------------

# closure to get property that trigged the main update function
def update_base_color_settings_closure(prop):
    return lambda a,b: update_color_settings(a,b,prop)

def update_color_settings(self, context, origin=""):
    
    if hasattr(self,'block_auto_update'):
        if self.block_auto_update:
            return

    objs = context.selected_objects
    props = context.scene.principledtools
    
    # Checking for color helper nodes
    
    nodes_groups_helpers = []
    principled_nodes = []

    if props.enum_materials == '0':

        for ob in objs:
            if ob.data.materials:
                for mat in ob.data.materials:
                    if not mat.use_nodes:
                        active_use_nodes(mat)

                    for nod in mat.node_tree.nodes:
                        if nod.type == 'GROUP':
                            if nod.name.endswith(node_identifier):                   
                                nodes_groups_helpers.append(nod)
                        if nod.type == 'BSDF_PRINCIPLED':
                                principled_nodes.append(nod)

    
    if props.enum_materials == '1':
        
        if context.active_object:
            mat = context.active_object.active_material
            if mat:
                if not mat.use_nodes:
                    active_use_nodes(mat)

                for nod in context.active_object.active_material.node_tree.nodes:
                    if nod.type == 'GROUP':
                        if nod.name.endswith(node_identifier):                   
                            nodes_groups_helpers.append(nod)
                    if nod.type == 'BSDF_PRINCIPLED':
                        principled_nodes.append(nod)

    if origin == 'HUE':
        props.use_b_hue = True
    if origin == 'SATURATION':
        props.use_b_saturation = True 
    if origin == 'VALUE':
        props.use_b_value = True 
    
    if origin == 'BRIGHT':
        props.use_b_bright = True 
    if origin == 'CONTRAST':
        props.use_b_contrast = True 
    
    if origin == 'GAMMA':
        props.use_b_gamma = True 
        
    if origin == 'USE MIX':
        props.use_b_use_color_mix = True 
    if origin == 'MIX FAC':
        props.use_b_color_mix_fac = True  
        
    # Only when using HSV 
         
    # It will create a color group node in each principled node when inputs like HUE, SATURATION, VALUE where trigged but none of this nodes was created
       
    if not True in (props.use_b_hue,
                props.use_b_saturation,
                props.use_b_value,
                props.use_base_color,
                props.use_b_contrast,
                props.use_b_bright,
                props.use_b_gamma):
        return
        
    if props.auto_update or origin == 'All':
        
        # TODO Remove "If not nodes_groups_helpers", se não em caso que não existe apenas um, ele ignora
        
        if not nodes_groups_helpers:
            
            # Create color helper group node
            for p_node in principled_nodes:
                
                mix_group = base_color_helper(p_node.id_data, p_node.inputs[0],props.p_base_color,p_node)
                                    
                if not props.use_base_color:
                    # Mute mix node when there is no base color update
                    for node in mix_group.node_tree.nodes:
                        if node.type == 'MIX_RGB':
                            node.mute = True        
                            
                nodes_groups_helpers.append(mix_group)
            
    for node in nodes_groups_helpers:
        
        if not node:
            continue
            
        for n in node.node_tree.nodes:      
            if n.type == 'MIX_RGB':

                if origin == 'USE MIX' and props.auto_update or origin == 'All':
                    if props.use_b_use_color_mix:
                        if not props.b_use_color_mix:
                            n.inputs[0].default_value = 0
                        else:                     
                            n.inputs[0].default_value = props.b_color_mix_fac
    
                if props.b_use_color_mix:
                    if origin == 'MIX FAC' and props.auto_update or origin == 'All':
                        if props.use_b_color_mix_fac:
                            n.inputs[0].default_value = props.b_color_mix_fac
                
                # Only when auto update is off
                
                # The base color updates only the main operator is confirmed, while the other props of the mixing color operation
                # are update when the mixing color operator is confirmed
                # that's why was necessary to manually set the base color when the mixing color operation is confirmed
                if origin == 'All':
                    if props.use_base_color:
                        n.inputs[2].default_value = props.p_base_color

                continue

            if n.type == 'HUE_SAT':

                if origin == 'HUE' and props.auto_update or origin == 'All':
                    if props.use_b_hue:
                        n.inputs[0].default_value = props.b_hue
                
                if origin == 'SATURATION' and props.auto_update  or origin == 'All':
                    if props.use_b_saturation:
                        n.inputs[1].default_value = props.b_saturation
                    
                if origin == 'VALUE' and props.auto_update  or origin == 'All':
                    if props.use_b_value:
                        n.inputs[2].default_value = props.b_value   
                
                continue 
                
            if n.type == 'BRIGHTCONTRAST':

                if origin == 'BRIGHT' and props.auto_update or origin == 'All':
                    if props.use_b_bright:
                        n.inputs[1].default_value = props.b_bright
                
                if origin == 'CONTRAST' and props.auto_update  or origin == 'All':
                    if props.use_b_contrast:
                        n.inputs[2].default_value = props.b_contrast
                                        
                continue
            
            if n.type == 'GAMMA':

                if origin == 'GAMMA' and props.auto_update or origin == 'All':
                    if props.use_b_gamma:
                        n.inputs[1].default_value = props.b_gamma
                                                            
                continue 

# -------------------------------------------------------------
# Extra Function Updates
# -------------------------------------------------------------

# Update principled nodes count  
def update_enum_materials_node_count(self,context):
    self.principled_nodes_found = len(get_principled_nodes())
    self.show_base_color_extras = check_if_linked_base_color()
    
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


    






