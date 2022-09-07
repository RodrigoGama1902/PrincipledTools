import bpy
import os
import json

from ..property.addon_props import activate_selected_preset, update_main_props
from ..utility.constants import *
from ..utility.functions import (json_check,
                                generate_preset_data,
                                write_preset_json,
                                )

def draw_presets_ui(self,layout):
    
    props = bpy.context.scene.principledtools
    
    box = layout.box()
    box.label(text='Principled Node Setups')
    box.operator('pt.quickbump')
    box.operator('pt.quicktranslucent')
    
    row = layout.row(align=True)
    row.label(text='Principled Presets')
    row.operator('pt.addnewpreset',text='',icon='PRESET_NEW')
    
    preset_col = layout.column(align=True)
    
    for i in props.loaded_presets:
        row = preset_col.row(align=True)
        row.operator("pt.activatepreset",text=i.preset_name).preset_name = i.preset_name
        row.operator("pt.removepreset", text='', icon='X').preset_name = i.preset_name
                    
class PT_PresetSystem(bpy.types.Operator): # change material props from mp 
    """Use Preset"""

    bl_idname = "pt.presetsystem"
    bl_label = "Use Preset"
    bl_options = {'REGISTER','UNDO'}

    prop_test : bpy.props.BoolProperty() #type:ignore

    @classmethod
    def poll(cls, context):
        if bpy.context.active_object:
            return True

    def execute(self, context):

        return {'FINISHED'}

    def invoke(self, context, event):
        
        generate_preset_data()
        
        default_x = event.mouse_x
        default_y = event.mouse_y

        context.window.cursor_warp(default_x + 35, default_y + 20)
        context.window_manager.invoke_popup(self, width=220)
        context.window.cursor_warp(default_x, default_y)

        return {'RUNNING_MODAL'}

        #return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):

        layout = self.layout
        draw_presets_ui(self,layout)

class PT_ActivatePreset(bpy.types.Operator): # change material props from mp 
    """Activate Preset"""

    bl_idname = "pt.activatepreset"
    bl_label = "Activate Preset"
    bl_options = {'REGISTER', 'INTERNAL'}

    preset_name : bpy.props.StringProperty(default = "") #type:ignore
       
    def execute(self, context):
        
        activate_selected_preset(self, context, self.preset_name)
        
        props = bpy.context.scene.principledtools    
        props.last_active_preset = self.preset_name
        
        self.report({'INFO'},"Preset Loaded")
        return {'FINISHED'}
                  
class PT_ActivateLastPreset(bpy.types.Operator): 
    """Activate Last Preset"""

    bl_idname = "pt.activatelastpreset"
    bl_label = "Activate Last Preset"
    bl_options = {'REGISTER', 'INTERNAL'}
       
    def execute(self, context):
        
        props = bpy.context.scene.principledtools      
        preset_name = props.last_active_preset 
        
        if preset_name:
            activate_selected_preset(self, context, preset_name)
            update_main_props(self,context,'All')
            
        else:           
            self.report({'WARNING'},"No preset has been used yet")
            return {'CANCELLED'}
                  
        self.report({'INFO'},"Last Used Preset Loaded")
        return {'FINISHED'}

class PT_AddPPreset(bpy.types.Operator): # change material props from mp 
    """Save current principled setup as new preset"""

    bl_idname = "pt.addnewpreset"
    bl_label = "Save as Preset"
    bl_options = {'REGISTER', 'INTERNAL'}

    preset_name : bpy.props.StringProperty(default = "") #type:ignore
        
    def execute(self, context):
        
        props = bpy.context.scene.principledtools
        ignore_prop = ('Normal')
        
        prop_data = {}
        
        for i in props.__annotations__:
            if i.startswith('p_'):
                prop_name = i[2:]
                prop_bool = "use_" + prop_name
                
                if getattr(props,prop_bool):
                
                    prop_name = prop_name.replace('_',' ').title()
                                    
                    if prop_name == 'Ior':
                        prop_name = 'IOR'
                        
                    if prop_name in ignore_prop:
                        continue
                                                
                    if (round(getattr(props,i),2) if not prop_name in vector3_prop else getattr(props,i)) == principled_props_default[prop_name]:
                        continue
                    
                    prop_data[prop_name] = round(getattr(props,i),2) if not prop_name in vector3_prop else getattr(props,i)
        
        if prop_data:
                
            new_preset = props.loaded_presets.add()
            new_preset.preset_name = self.preset_name
            
            for p in prop_data:
                new_prop = new_preset.preset_prop_data.add()
                new_prop.prop_name = p
                
                if p == 'Base Color':
                    new_prop.prop_value_vector3 = prop_data[p]                  
                else:                  
                    new_prop.prop_value = prop_data[p]
        
            write_preset_json(context)
                                       
        self.report({'INFO'},"Preset Saved")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        
        default_x = event.mouse_x
        default_y = event.mouse_y

        context.window.cursor_warp(default_x + 145, default_y + 20)
        context.window_manager.invoke_props_dialog(self, width=220)
        context.window.cursor_warp(default_x, default_y)

        return {'RUNNING_MODAL'}

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        
        row = box.row()
        row.label(text='Preset Name')
        row = box.row()
        row.prop(self,'preset_name',text='')
        
class PT_RemovePreset(bpy.types.Operator): # change material props from mp 
    """Remove Preset"""

    bl_idname = "pt.removepreset"
    bl_label = "Remove Preset"
    bl_options = {'REGISTER', 'INTERNAL'}

    preset_name : bpy.props.StringProperty(default = "") #type:ignore
       
    def execute(self, context):
        
        props = bpy.context.scene.principledtools

        idx=-1
        for p in props.loaded_presets:
            idx+=1
            if p.preset_name == self.preset_name:
                props.loaded_presets.remove(idx)
        
        write_preset_json(context)
        
        self.report({'INFO'},"Preset Removed")        
        return {'FINISHED'}
    