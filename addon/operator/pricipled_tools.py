import bpy
import os
import json

from ..property.addon_props import update_props, update_color_settings
from ..utility.constants import *
from ..utility.functions import (
                                set_principled_default,
                                create_new_material,
                                set_base_color_default,
                                get_prefs,
                                check_if_linked_base_color,
                                get_principled_nodes,
                                get_all_nodes,
                                generate_preset_data
                                )

def draw_principled_update(self, layout):

    props = bpy.context.scene.principledtools
    prefs = get_prefs()
    
    col_mat_selection = layout.column(align=True)
    
    row_mat_selection = col_mat_selection.row(align=True)
    row_mat_selection.prop(props,'enum_materials',expand=True)
    
    box_mat_selection = col_mat_selection.box()
    row_box_mat_selection = box_mat_selection.row()
    row_box_mat_selection.label(text=f'Nodes Found: {str(props.principled_nodes_found)}')
    row_box_mat_selection.operator('pt.extraoptions',icon='SETTINGS',text='')
    
    # Extra Widgets
    
    if prefs.widget_new_material:
    
        box = layout.box()

        row = box.row()
        split_row = row.split(factor=0.91)
        split_row.label(text='New Material')
        split_row.operator('pt.creatematerial',text='',icon='MATERIAL')
    
    # Main Principled Props BOX

    box = layout.box()

    row = box.row()
    split_row = row.split(factor=0.91)
    split_row.label(text='Principled BSDF')
    split_row.operator("pt.presetsystem",text='',icon='PRESET')
    
    # Ui when found material with node linked in base color input
    
    if prefs.show_pi_base_color:
        
        row = box.row(align=True)
        box_color = row.box()
        
        if props.show_base_color_extras:
            show_prop_row = row.row(align=True)
            show_prop_row.scale_y = 1.5
            show_prop_row.operator('pt.basecolorsettings',text='',icon='TRIA_RIGHT')
    
        box_color_row = box_color.row()
        box_color_row.active = props.use_base_color
        box_color_row.prop(props,'p_base_color')
        
    if prefs.show_pi_subsurface:

        row = box.row()
        row.active = props.use_subsurface
        row.prop(props,'p_subsurface',slider=True)
    
    if prefs.show_pi_subsurface_ior:

        row = box.row()
        row.active = props.use_subsurface_ior
        row.prop(props,'p_subsurface_ior',slider=True)
    
    if prefs.show_pi_subsurface_anisotropy:

        row = box.row()
        row.active = props.use_subsurface_anisotropy
        row.prop(props,'p_subsurface_anisotropy',slider=True)
    
    if prefs.show_pi_metallic:

        row = box.row()
        row.active = props.use_metallic
        row.prop(props,'p_metallic',slider=True) 
    
    if prefs.show_pi_specular:

        row = box.row()
        row.active = props.use_specular
        row.prop(props,'p_specular',slider=True) 
    
    if prefs.show_pi_specular_tint:

        row = box.row()
        row.active = props.use_specular_tint
        row.prop(props,'p_specular_tint',slider=True) 
        
    if prefs.show_pi_roughness:

        row = box.row()
        row.active = props.use_roughness
        row.prop(props,'p_roughness',slider=True)
    
    if prefs.show_pi_anisotropic:

        row = box.row()
        row.active = props.use_anisotropic
        row.prop(props,'p_anisotropic',slider=True)

    if prefs.show_pi_anisotropic_rotation:

        row = box.row()
        row.active = props.use_anisotropic_rotation
        row.prop(props,'p_anisotropic_rotation',slider=True)
        
    if prefs.show_pi_sheen:

        row = box.row()
        row.active = props.use_sheen
        row.prop(props,'p_sheen',slider=True)
    
    if prefs.show_pi_sheen_tint:

        row = box.row()
        row.active = props.use_sheen_tint
        row.prop(props,'p_sheen_tint',slider=True)
    
    if prefs.show_pi_clearcoat:

        row = box.row()
        row.active = props.use_clearcoat
        row.prop(props,'p_clearcoat',slider=True)
    
    if prefs.show_pi_clearcoat_roughness:

        row = box.row()
        row.active = props.use_clearcoat_roughness
        row.prop(props,'p_clearcoat_roughness',slider=True)
    
    if prefs.show_pi_ior:

        row = box.row()
        row.active = props.use_ior
        row.prop(props,'p_ior')
    
    if prefs.show_pi_transmission:

        row = box.row()
        row.active = props.use_transmission
        row.prop(props,'p_transmission',slider=True)
    
    if prefs.show_pi_transmission_roughness:

        row = box.row()
        row.active = props.use_transmission_roughness
        row.prop(props,'p_transmission_roughness',slider=True)
    
    if prefs.show_pi_emission_strength:

        row = box.row()
        row.active = props.use_emission_strength
        row.prop(props,'p_emission_strength',slider=True)
    
    if prefs.show_pi_alpha:

        row = box.row()
        row.active = props.use_alpha
        row.prop(props,'p_alpha',slider=True)
    
    if prefs.show_pi_normal:

        row = box.row()
        row.active = props.use_normal
        row.prop(props,'p_normal',slider=False)
                                    
class PT_MainPrincipledTool(bpy.types.Operator): # change material props from mp 
    """Principled Tools"""

    bl_idname = "pt.maintools"
    bl_label = "Principled Tools"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        ob = bpy.context.active_object
        if ob:
            if hasattr(ob.data,'materials'):
                return True

    def execute(self, context):

        update_props(self,context,'All')

        return {'FINISHED'}

    def invoke(self, context, event):
                
        props = bpy.context.scene.principledtools
        
        props.show_base_color_extras = check_if_linked_base_color()
        props.principled_nodes_found = len(get_principled_nodes())

        set_base_color_default()
        set_principled_default()
        
        # Generate all principled presets in JSON file
        generate_preset_data()

        # Set all principled props bool to False, it's necessary because after setting to default with these functions above,
        # all props will be updated
        for i in props.keys():
            if i.startswith('use_'):
                setattr(props, i, False)
         
        return context.window_manager.invoke_props_dialog(self, width=250)

    def draw(self, context):

        layout = self.layout
        draw_principled_update(self, layout)

class PT_OP_CreateNewMaterial(bpy.types.Operator): # change material props from mp 
    """Activate Preset"""

    bl_idname = "pt.creatematerial"
    bl_label = "Create New Material"
    bl_options = {'REGISTER', 'INTERNAL'}

    material_name : bpy.props.StringProperty(default = "Material") # type:ignore

    def execute(self, context):

        objs = bpy.context.selected_objects
        ob = bpy.context.active_object

        create_new_material(ob,self.material_name)
                               
        return {'FINISHED'}
    
    def invoke(self, context, event):
        
        default_x = event.mouse_x
        default_y = event.mouse_y

        context.window.cursor_warp(default_x + 145, default_y + 20)
        context.window_manager.invoke_props_dialog(self, width=220)
        context.window.cursor_warp(default_x, default_y)

        return {'RUNNING_MODAL'}

        #return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):

        layout = self.layout
        
        box = layout.box()
        
        row = box.row()
        row.label(text='Material Name')
        row = box.row()
        row.prop(self,'material_name',text='')

class PT_OP_BaseColorSettings(bpy.types.Operator):
    """Base Color Settings"""

    bl_idname = "pt.basecolorsettings"
    bl_label = "Color Mixing Settings"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if bpy.context.active_object:
            return True

    def execute(self, context):

        update_color_settings(self, context, 'All')

        return {'FINISHED'}

    def invoke(self, context, event):

        #props = bpy.context.scene.principledtools

        # Set all principled props bool to False
        #for i in props.keys():
        #    if i.startswith('use_b'):
        #        setattr(props, i, False)
        
        default_x = event.mouse_x
        default_y = event.mouse_y

        context.window.cursor_warp(default_x + 145, default_y + 20)
        context.window_manager.invoke_props_dialog(self, width=220)
        context.window.cursor_warp(default_x, default_y)

        return {'RUNNING_MODAL'}

    def draw(self, context):

        layout = self.layout
        props = bpy.context.scene.principledtools

        #box = layout.box()
        #row = box.row()
        #row.prop(props,'p_base_color')
        
        box = layout.box()
        #box.label(text='Color Mix')
        
        row = box.row()
        
        color_row = box.row() 
        color_row.active = props.use_base_color    
        color_row.prop(props,'p_base_color')
        
        row = box.row()
        row.active = props.use_b_color_mix_fac
        row.prop(props,'b_color_mix_fac',slider=True)

        box = layout.box()
        box.label(text='HSV')

        row = box.row()
        row.active = props.use_b_hue
        row.prop(props,'b_hue',slider=True)

        row = box.row()
        row.active = props.use_b_saturation
        row.prop(props,'b_saturation',slider=True)

        row = box.row()
        row.active = props.use_b_value
        row.prop(props,'b_value',slider=True)
        
        box = layout.box()
        box.label(text='Bright/Contrast')

        row = box.row()
        row.active = props.use_b_bright
        row.prop(props,'b_bright')

        row = box.row()
        row.active = props.use_b_contrast
        row.prop(props,'b_contrast')
        
        box = layout.box()
        box.label(text='Gamma')

        row = box.row()
        row.active = props.use_b_gamma
        row.prop(props,'b_gamma')

class PT_OP_RemoveHelperNodes(bpy.types.Operator):
    """Remove Helper Nodes"""

    bl_idname = "pt.removehelpers"
    bl_label = "Remove Helper Nodes"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if bpy.context.active_object:
            return True
    
    def remove_and_relink(self,node):
        
        node_tree = node.id_data 
        relinked = False
        
        before_socket = None
        for i in node.inputs:
            if i.links:
                before_socket = i.links[0].from_socket
        
        to_socket = None
        for i in node.outputs:
            if i.links:
                to_socket = i.links[0].to_socket
        
        if before_socket and to_socket:
            
            link = node_tree.links.new
            link(before_socket, to_socket)   
            
            relinked = True   
        
        if relinked:
            node_tree.nodes.remove(node)
    
    def execute(self, context):

        nodes = get_principled_nodes()
        node_trees = (nt.id_data for nt in nodes)
        
        for nt in node_trees:   
            nt_nodes = get_all_nodes(nt)      
            for n in nt_nodes:
                if node_identifier in n.name:
                    self.remove_and_relink(n)
            
        return {'FINISHED'}          

class PT_OP_ExtraOptions(bpy.types.Operator): # change material props from mp 
    """Extra Options"""

    bl_idname = "pt.extraoptions"
    bl_label = "Extra Options"
    bl_options = {'REGISTER','UNDO'}
    
    @classmethod
    def poll(cls, context):
        if bpy.context.active_object:
            return True

    def execute(self, context):
        pass
        return {'FINISHED'}

    def invoke(self, context, event):
        
        default_x = event.mouse_x
        default_y = event.mouse_y

        context.window.cursor_warp(default_x + 35, default_y + 20)
        context.window_manager.invoke_popup(self, width=220)
        context.window.cursor_warp(default_x, default_y)

        return {'RUNNING_MODAL'}

    def draw(self, context):

        layout = self.layout
        props = bpy.context.scene.principledtools
        
        layout.label(text='Extra Options')
        
        box = layout.box()      
        row = box.row()
        row.prop(props,'auto_update')
        
        layout.label(text='Extra Tools')
             
        row = layout.row()
        row.operator('pt.removehelpers')
        row = layout.row(align=True)
        row.operator('pt.smartmaterialsetup').rule_settings = False
        row.operator('pt.manageignoredmaterials', text='', icon='FILE_REFRESH').action = "REMOVE"
        row.operator('pt.smartmaterialsetup', text='', icon='GREASEPENCIL').rule_settings = True

        









        
