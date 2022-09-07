#type: ignore

import bpy

from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)

from ..utility.constants import addon_name
from ..utility.functions import get_prefs


class PT_AddonPrefs(bpy.types.AddonPreferences):    
    bl_idname = addon_name

    ###### Preferences
    
    show_pi_props_in_prefs : bpy.props.BoolProperty(name='Show Props',default=True) 
    
    # Pi = Principled Input
    
    show_pi_base_color : bpy.props.BoolProperty(name='Base Color',default=True) 
    show_pi_subsurface : bpy.props.BoolProperty(name='Subsurface',default=False)
    show_pi_subsurface_ior : bpy.props.BoolProperty(name='Subsurface IOR',default=False)
    show_pi_subsurface_anisotropy : bpy.props.BoolProperty(name='Subsurface Anisotropy',default=False)
    show_pi_metallic : bpy.props.BoolProperty(name='Metallic',default=True)
    show_pi_specular : bpy.props.BoolProperty(name='Specular',default=True)
    show_pi_specular_tint : bpy.props.BoolProperty(name='Specular Tint',default=False)
    show_pi_roughness : bpy.props.BoolProperty(name='Roughness',default=True)
    show_pi_anisotropic : bpy.props.BoolProperty(name='Anisotropic',default=True)
    show_pi_anisotropic_rotation : bpy.props.BoolProperty(name='Anisotropic Rotation',default=False)
    show_pi_sheen : bpy.props.BoolProperty(name='Sheen',default=True)
    show_pi_sheen_tint : bpy.props.BoolProperty(name='Sheen Tint',default=False)
    show_pi_clearcoat : bpy.props.BoolProperty(name='Clearcoat',default=False)
    show_pi_clearcoat_roughness : bpy.props.BoolProperty(name='Clearcoat Roughness',default=False)
    show_pi_ior : bpy.props.BoolProperty(name='IOR',default=False)
    show_pi_transmission: bpy.props.BoolProperty(name='Transmission',default=True)
    show_pi_transmission_roughness: bpy.props.BoolProperty(name='Transmission Roughness',default=True)
    show_pi_emission_strength: bpy.props.BoolProperty(name='Emission Strength',default=True)
    show_pi_alpha: bpy.props.BoolProperty(name='Alpha',default=True)
    show_pi_normal: bpy.props.BoolProperty(name='Normal',default=True)
    
    # Auto Create New Material
    
    auto_new_material : bpy.props.BoolProperty(name='Create New Material When Necessary',description="Creates a new material in all selected objects that has no material when using principled tools",default=True)
    
    # Extra Widgets
    
    widget_new_material : bpy.props.BoolProperty(name='New Material',default=False)
    
    # Smart materials
    
    store_materials_sms : bpy.props.BoolProperty(name='Ignore Configured Materials',description="Store all materials that has been configured with Smart Material Setup, so when SMS run again, these materials will not be updated until you refresh the SMS stored materials list", default=True)
    
    def draw(self, context):

        prefs = get_prefs()
        layout = self.layout
        
        box = layout.box()
        box.label(text='Principled Tools')
        p_row = box.row()
        p_row.prop(prefs, "auto_new_material")
        
        box = layout.box()
        box.label(text='Smart Material Setup')
        p_row = box.row()
        p_row.prop(prefs, "store_materials_sms")
        
        box = layout.box()
        box.label(text='Extra Widgets')
        p_row = box.row()
        p_row.prop(prefs, "widget_new_material")
        
        box = layout.box()
        props_row = box.row()
        props_row.label(text='Active Principled Inputs')
        props_row.prop(prefs, "show_pi_props_in_prefs", text="", icon="TRIA_DOWN")
               
        if prefs.show_pi_props_in_prefs:
               
          for p in self.__annotations__:
            if p.startswith('show_pi_'):
              if hasattr(prefs,p):
                p_row = box.row()
                p_row.active = getattr(prefs,p)
                p_row.prop(prefs, p)
              
              
              


      

        