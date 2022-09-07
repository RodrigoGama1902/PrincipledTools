#type: ignore

import bpy

from bpy.props import (
                       BoolProperty,
                       )

from ..utility.constants import ADDON_NAME
from .draw_addon_preferences import draw_addon_preferences


class PT_AddonPrefs(bpy.types.AddonPreferences):    
    bl_idname = ADDON_NAME

    show_pi_props_in_prefs : BoolProperty(name='Show Props',default=True) 
    
    # Pi = Principled Input
    
    show_pi_base_color : BoolProperty(name='Base Color',default=True) 
    show_pi_subsurface : BoolProperty(name='Subsurface',default=False)
    show_pi_subsurface_ior : BoolProperty(name='Subsurface IOR',default=False)
    show_pi_subsurface_anisotropy : BoolProperty(name='Subsurface Anisotropy',default=False)
    show_pi_metallic : BoolProperty(name='Metallic',default=True)
    show_pi_specular : BoolProperty(name='Specular',default=True)
    show_pi_specular_tint : BoolProperty(name='Specular Tint',default=False)
    show_pi_roughness : BoolProperty(name='Roughness',default=True)
    show_pi_anisotropic : BoolProperty(name='Anisotropic',default=True)
    show_pi_anisotropic_rotation : BoolProperty(name='Anisotropic Rotation',default=False)
    show_pi_sheen : BoolProperty(name='Sheen',default=True)
    show_pi_sheen_tint : BoolProperty(name='Sheen Tint',default=False)
    show_pi_clearcoat : BoolProperty(name='Clearcoat',default=False)
    show_pi_clearcoat_roughness : BoolProperty(name='Clearcoat Roughness',default=False)
    show_pi_ior : BoolProperty(name='IOR',default=False)
    show_pi_transmission: BoolProperty(name='Transmission',default=True)
    show_pi_transmission_roughness: BoolProperty(name='Transmission Roughness',default=True)
    show_pi_emission_strength: BoolProperty(name='Emission Strength',default=True)
    show_pi_alpha: BoolProperty(name='Alpha',default=True)
    show_pi_normal: BoolProperty(name='Normal',default=True)
    

    auto_new_material : BoolProperty(name='Create New Material When Necessary',description="Creates a new material in all selected objects that has no material when using principled tools",default=True)
      
    widget_new_material : BoolProperty(name='New Material',default=False)
    
    store_materials_sms : BoolProperty(name='Ignore Configured Materials',description="Store all materials that has been configured with Smart Material Setup, so when SMS run again, these materials will not be updated until you refresh the SMS stored materials list", default=True)
    
    def draw(self, context):
      draw_addon_preferences(self, context)

        
              
              
              


      

        