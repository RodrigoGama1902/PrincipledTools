import bpy
import pathlib
import os

addon_name = __name__.partition('.')[0]

command_file_name = 'principled_presets.json'
favorites_path = os.path.join(os.path.dirname(pathlib.Path(__file__).parent.absolute()), command_file_name)

smart_mat_s_name = 'principled_smartmat_presets.json'
smart_mat_s_path = os.path.join(os.path.dirname(pathlib.Path(__file__).parent.absolute()), smart_mat_s_name)

smart_mat_s_name_test = 'principled_smart_mat_presets_test.json'
smart_mat_s_path_test = os.path.join(os.path.dirname(pathlib.Path(__file__).parent.absolute()), smart_mat_s_name_test)

node_identifier = '_PRINCIPLEDTOOLSNODE'

multiply_node_name = 'MULTIPLY' + node_identifier
mix_node_name = 'MIX' + node_identifier
hue_node_name = 'HUE' + node_identifier
bc_node_name = 'BC' + node_identifier
gamma_node_name = 'GAMMA' + node_identifier
mix_color_group = 'MIXING_GROUP' + node_identifier

principled_props_default = {
    'Base Color': (0.800000011920929,0.800000011920929,0.800000011920929,1),
    'Alpha' : 1,
    'Anisotropic' : 0,
    'Anisotropic Rotation' : 0,
    'Clearcoat' : 0,
    'Clearcoat Roughness' : 0.03,
    'Emission Strength' : 1,
    'IOR' : 1.450,
    'Metallic' : 0,
    'Roughness' : 0.5,
    'Sheen' : 0,
    'Sheen Tint' : 0.5,
    'Specular' : 0.5,
    'Specular Tint' : 0,
    'Subsurface' : 0,
    'Transmission' : 0,
    'Transmission Roughness' : 0,    
}

vector3_prop = ["Base Color", "Emission"]


