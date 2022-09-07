import bpy
import pathlib
import os

ADDON_NAME = __name__.partition('.')[0]

COMMAND_FILE_NAME = 'principled_presets.json'
FAVORITES_PATH = os.path.join(os.path.dirname(pathlib.Path(__file__).parent.absolute()), COMMAND_FILE_NAME)

SMART_MATERIAL_PRESETS_FILENAME = 'principled_smartmat_presets.json'
SMART_MATERIAL_PRESETS_PATH = os.path.join(os.path.dirname(pathlib.Path(__file__).parent.absolute()), SMART_MATERIAL_PRESETS_FILENAME)

SMART_MATERIAL_PRESETS_TEST_FILENAME = 'principled_smart_mat_presets_test.json'
SMART_MATERIAL_PRESETS_TEST_PATH = os.path.join(os.path.dirname(pathlib.Path(__file__).parent.absolute()), SMART_MATERIAL_PRESETS_TEST_FILENAME)

ADDON_NODE_IDENTIFIER = '_PRINCIPLEDTOOLSNODE'

RGB_NODE_NAME = 'RGB' + ADDON_NODE_IDENTIFIER
MULTIPLY_NODE_NAME = 'MULTIPLY' + ADDON_NODE_IDENTIFIER
MIX_NODE_NAME = 'MIX' + ADDON_NODE_IDENTIFIER
HUE_NODE_NAME = 'HUE' + ADDON_NODE_IDENTIFIER
BC_NODE_NAME = 'BC' + ADDON_NODE_IDENTIFIER
GAMMA_NODE_NAME = 'GAMMA' + ADDON_NODE_IDENTIFIER
MIX_COLOR_GROUP_NAME = 'MIXING_GROUP' + ADDON_NODE_IDENTIFIER

PRINCIPLED_PROPS_DEFAULT = {
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

VECTOR3_PROP = ["Base Color", "Emission"]


