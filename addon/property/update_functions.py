import bpy

from .update_functions import *
from ..utility.constants import *
from ..utility.constants import *
from ..utility.functions import (
                                 get_principled_nodes,
                                 check_if_linked_base_color,
                                 create_mixing_color_group,
                                 set_principled_default,
                                 reset_principled_node,
                                 reset_principled_node_preset,
                                 get_context_materials)    

def activate_selected_preset(self, context, preset_name, principled = None, load_mode = 'UPDATE_PROP'):
        
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
  
                                
def base_color_helper(context, node_tree, input,value,principled):
    '''Returns the base color helper group, creates one if necessary'''
    
    default_x_offset = principled.location[0] -150

    y_input_locations = {
        'Base Color': (default_x_offset, principled.location[1] - 105),     
    }
    
    # Checking if other nodes has connected base color
    principled_nodes = get_principled_nodes(context)
    has_base_color_link = False
    
    for node in principled_nodes:
        if node.inputs[input.name].links:
            has_base_color_link = True
    
    # If other node has linked base color, creates and RGB input node, so settings like HSV can be changed
    if has_base_color_link and not input.links:
        
        rgb_input = node_tree.nodes.new('ShaderNodeRGB')
        rgb_input.name = rgb_node_name 
        rgb_input.outputs[0].default_value = input.default_value
        rgb_input.location = (y_input_locations['Base Color'][0] - 150,y_input_locations['Base Color'][1])
        rgb_input.hide = True
            
        link = node_tree.links.new
        link(rgb_input.outputs[0], input) 
        
    mix_group = None
    
    if input.links: 
        # Checking if basecolor is connected to any node
        
        if not input.links[0].from_node.name.startswith(mix_color_group):    
            # If connected to any node other than Mix Color Group, creates Mix Color Group
            
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
            # Else, just update the Mix Color Group input value
            mix_group = input.links[0].from_node
            
        # Getting the mix_node inside the Mix Color Group                             
        mix_node = [n for n in mix_group.node_tree.nodes if n.type == 'MIX_RGB']
        
        if mix_node:
            mix_node = mix_node[0]              
            mix_node.inputs[2].default_value = value 

    else:
        # If not connected, just set base color to input value
        if value:
            input.default_value = value
            
    return mix_group


def math_node_helper(node_tree, input,value,principled):
        
    def constant_y_position(y_index, base_y = 189):
        '''Generate correct y position using y-index from node input'''
        
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


def update_normal_principled_input(self, input, origin, node_tree, principled):
    '''Update normal input prop (Only used when principled prop name is 'Normal')'''

    def update_found_normal_node(from_node, from_socket):   
        '''Function used to find and modify bump or normal map node
        
        This is function is recursion ready, meaning the sometimes will get group node and normal/bump nodes

        If the node is bump/normal, this function will skip the process of find normal/bump nodes inside group
        if the node is group type, will run this task below to find bump/normal nodes'''

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

            for i in g_output.inputs: # type: ignore

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
                        from_socket_node, from_socket_socket = ignore_reroute_node(from_socket_node) #type: ignore
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
                update_found_normal_node(from_socket_node, from_socket_socket) #type: ignore
    
    i = input

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


def update_single_principled_prop(self, context, input, origin, node_tree, principled, prop_name):
    '''This function will automatically update each principled prop by it input name'''

    i = input
    n = principled 

    props = context.scene.principledtools
    
    prop_name = prop_name.replace(' ','_') # Replace empty spaces like in "Transmission Roughness"

    prop = getattr(props,'p_' + prop_name)
    prop_bool = getattr(props,'use_' + prop_name)

    if i.name == origin: # if True, means that this property is changing real time, so the prop bool should be set to True
        setattr(props,'use_' + prop_name, True)
        
    if props.auto_update or origin == 'All': # If True, means that the update_props function is running through operator or through auto update                
        if prop_bool:  
            if prop_name == 'base_color':   # Base color update is different than simple props updates that will use math node helpers                 
                base_color_helper(context, node_tree, i, prop,n)
            else:            
                math_node_helper(node_tree, i, prop,n)
        
  
def update_props(self,context,origin):
    '''Main Update Props Function'''
    
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
                                  
                    update_single_principled_prop(self, context, i, origin, node_tree, n, i.name.lower())
                
                if i.name == 'Normal':

                    update_normal_principled_input(self, i, origin, node_tree, n)
                    
# -------------------------------------------------------------
# Base Color Settings
# -------------------------------------------------------------

def update_color_settings(self, context, origin=""):
    '''Handles the color property updates, such as color_mix, hue, saturation, value, etc'''
    
    if hasattr(self,'block_auto_update'):
        if self.block_auto_update:
            return
        
    props = context.scene.principledtools
    
    # Checking for color helper nodes
    
    nodes_groups_helpers = []
    principled_nodes = get_principled_nodes(create_materials = False)

    if origin == 'Hue':
        props.use_b_hue = True
    if origin == 'Saturation':
        props.use_b_saturation = True 
    if origin == 'Value':
        props.use_b_value = True 
    
    if origin == 'Bright':
        props.use_b_bright = True 
    if origin == 'Contrast':
        props.use_b_contrast = True 
    
    if origin == 'Gamma':
        props.use_b_gamma = True        
    if origin == 'Color Mix Fac':
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
        
        # Create color helper group node
        for p_node in principled_nodes:         
            mix_group = base_color_helper(context, p_node.id_data, p_node.inputs[0],props.p_base_color,p_node)             
            nodes_groups_helpers.append(mix_group)
            
    for node in nodes_groups_helpers:
        
        if not node:
            continue
                    
        for n in node.node_tree.nodes:      
            if n.type == 'MIX_RGB':    
                   
                if origin == 'Color Mix Fac' and (props.auto_update or origin == 'All'):
                    n.inputs[0].default_value = props.b_color_mix_fac
            
                continue

            if n.type == 'HUE_SAT':

                if origin == 'Hue' and props.auto_update or origin == 'All':
                    if props.use_b_hue:
                        n.inputs[0].default_value = props.b_hue
                
                if origin == 'Saturation' and props.auto_update  or origin == 'All':
                    if props.use_b_saturation:
                        n.inputs[1].default_value = props.b_saturation
                    
                if origin == 'Value' and props.auto_update  or origin == 'All':
                    if props.use_b_value:
                        n.inputs[2].default_value = props.b_value   
                
                continue              
                
            if n.type == 'BRIGHTCONTRAST':

                if origin == 'Bright' and props.auto_update or origin == 'All':
                    if props.use_b_bright:
                        n.inputs[1].default_value = props.b_bright
                
                if origin == 'Contrast' and props.auto_update  or origin == 'All':
                    if props.use_b_contrast:
                        n.inputs[2].default_value = props.b_contrast
                                        
                continue     
            
            if n.type == 'GAMMA':

                if origin == 'Gamma' and props.auto_update or origin == 'All':
                    if props.use_b_gamma:
                        n.inputs[1].default_value = props.b_gamma
                                                            
                continue

# -------------------------------------------------------------
# Extra Function Updates
# -------------------------------------------------------------

def update_enum_materials_node_count(self,context):
    '''Update principled nodes count'''
    
    self.principled_nodes_found = len(get_principled_nodes())
    self.show_base_color_extras = check_if_linked_base_color()
 