import bpy
import os
import json

from ..property.addon_props import activate_selected_preset, update_preset_enum_prop
from .node_operators import create_quick_bump, create_quick_translucent
from ..utility.constants import *
from ..utility.functions import (
                                generate_smart_preset_data,
                                active_use_nodes,
                                reset_principled_node,
                                write_smart_mat_json,
                                get_prefs
                                )


def draw_smart_mat_presets_ui(self,layout):

    empty_favorites = False
    props = bpy.context.scene.principledtools
    
    #smart_material_setup_presets
    main_row = layout.row()
    main_box = main_row.box()
    
    row_main_box = main_box.row()
    row_main_box.label(text='Smart Material Setup') 
    row_main_box.prop(props,'toggle_preset_edit', text='',icon='GREASEPENCIL')
    row_main_box.operator('pt.addsms', text='',icon='PRESET_NEW')
    
    ui_list_row = main_box.row()
    smart_col = ui_list_row.column(align=True)
      
    smart_col.template_list("PT_SMS_UL_items", "", props, "smart_material_setup_presets", props, "sms_custom_index", rows=8)
    
    if props.toggle_preset_edit:        
        edit_box = smart_col.box()
        
        sms = props.smart_material_setup_presets[props.sms_custom_index]
        
        if sms:
        
            edit_box.prop(sms,'smart_preset_name')       
            edit_box.prop(sms,'preset_to_activate') 
            edit_box.prop(sms,'select_node_setup') 
                        
            name_detect = edit_box.box()
            name_detect_row = name_detect.row()           
            name_detect_row.prop(sms,"use_name_detect")
            
            if sms.use_name_detect:
                
                name_detect_row.prop(sms,"name_detect_operation", text='')
                rbg_detect_row = name_detect.row()              
                rbg_detect_row.prop(sms,'material_string')  
                           
            rgb_detect = edit_box.box()
            rbg_detect_row = rgb_detect.row()           
            rbg_detect_row.prop(sms,"use_rgb_detect")
                                     
            if sms.use_rgb_detect:
                
                rbg_detect_row.prop(sms,"rgb_operation", text='')
            
                rbg_detect_row = rgb_detect.row()
                    
                rbg_detect_row.prop(sms,'detect_r', text='')  
                rbg_detect_row.prop(sms,'r_value')
                rbg_detect_row.prop(sms,'r_operation', text='')       
                           
                rbg_detect_row = rgb_detect.row()
        
                rbg_detect_row.prop(sms,'detect_g', text='')  
                rbg_detect_row.prop(sms,'g_value')
                rbg_detect_row.prop(sms,'g_operation', text='')            
                           
                rbg_detect_row = rgb_detect.row()
                              
                rbg_detect_row.prop(sms,'detect_b', text='') 
                rbg_detect_row.prop(sms,'b_value')
                rbg_detect_row.prop(sms,'b_operation', text='') 
                
                rbg_detect_row = rgb_detect.row()
                
                rbg_detect_row.prop(sms,'detect_a', text='') 
                rbg_detect_row.prop(sms,'a_value')
                rbg_detect_row.prop(sms,'a_operation', text='') 
                
       
            # Prop detect
            
            prop_detect = edit_box.box()
            prop_detect_row = prop_detect.row()           
            prop_detect_row.prop(sms,"use_prop_detect")
            #prop_detect_row.prop(sms,"rgb_operation", text='')
                           
            if sms.use_prop_detect:
                
                prop_detect_row.prop(sms,"prop_detect_operation", text='')
                            
                prop_detect_row = prop_detect.row() 
                prop_detect_row.prop(sms,"prop_to_add", text="Add Property")
                
                action = prop_detect_row.operator("pt.managepropdetect", text='',icon='ADD')
                action.action = "ADD"
                action.smart_preset_name = sms.smart_preset_name
                action.add_preset = sms.prop_to_add
                      
                for i in sms.prop_data_detect:
                    prop_box = prop_detect.box()
                    prop_box_row = prop_box.row()
                    prop_box_row.label(text=i.prop_name)
                    prop_box_row.prop(i,'prop_value', text='')
                    prop_box_row.prop(i,'prop_operation', text='')
                    
                    action = prop_box_row.operator("pt.managepropdetect", text='',icon='X')
                    action.action = 'REMOVE'
                    action.smart_preset_name = sms.smart_preset_name
        
    tool_col = ui_list_row.column(align=True) 
    tool_col.operator("pt.moveitemsms",text='',icon='TRIA_UP').move = "UP"
    tool_col.operator("pt.moveitemsms",text='',icon='TRIA_DOWN').move = "DOWN"
       
class PT_SMS_UL_items(bpy.types.UIList):
    
    # detects if preset has any active find method
    def detect_find_method(self,item):
        
        if True in (item.use_name_detect, item.use_rgb_detect, item.use_prop_detect):
            return True
        else:
            return False
            

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        
        props = bpy.context.scene.principledtools
        
        layout.prop(item, 'active_preset', text='') 
        layout.prop(item, 'smart_preset_name', text='',emboss=False, translate=False) 
        #layout.prop(props,'toggle_preset_edit', text='',icon='GREASEPENCIL',emboss=False, translate=False)
        
        if not self.detect_find_method(item):       
            layout.label(text='',icon='ERROR')
            
        layout.operator('pt.removesms',text='',icon='X',emboss=False, translate=False).rule_name = item.smart_preset_name
        #layout.prop(item, 'preset_name', text='',emboss=False, translate=False)     
        #layout.label(text=item.preset_camera.name if item.preset_camera else 'None',icon='OUTLINER_OB_CAMERA') 
            
class PT_OP_SmartMaterialSetup(bpy.types.Operator):
    """Smart Material Setup"""

    bl_idname = "pt.smartmaterialsetup"
    bl_label = "Smart Material Setup"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if bpy.context.active_object:
            return True
        
    rule_settings : bpy.props.BoolProperty()
    
    def smart_material_setup(self,context):
                
        props = bpy.context.scene.principledtools
        prefs = get_prefs()
                
        objs = bpy.context.selected_objects
        done_materials = [] # Store materials that were already analyzed by SMS, so if this materials is found again in another object, it will be ignored
        
        for ob in objs:
            
            if hasattr(ob.data,'materials'):
                for mat in ob.data.materials:
                    # Ignore materials inside "Ignore materials collection"
                    if prefs.store_materials_sms:
                        if mat in [m.material_data for m in props.sms_ignore_materials] and not mat in done_materials:
                            continue
                    
                    if not mat in done_materials:
                        
                        detected_rule = None
                        material_detected = False
                        
                        active_use_nodes(mat)
                        
                        original_principled = [n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'][0]
                  
                        for rule in props.smart_material_setup_presets:
                            if rule.active_preset: # Detects if this preset is active 
                            
                                name_list = rule.material_string.split(',')
                                
                                # This 'gates' will be used to define the final condition of the execution of the current rule
                                rgb_gate = False
                                name_gate = False
                                prop_detect_gate = False
                                
                                # RGB Detect
                                
                                if rule.use_rgb_detect:
                                    if original_principled:
                                        
                                        r = original_principled.inputs[0].default_value[0]
                                        g = original_principled.inputs[0].default_value[1]
                                        b = original_principled.inputs[0].default_value[2]
                                        a = original_principled.inputs[0].default_value[3]
                                        
                                        true_r = True
                                        true_g = True
                                        true_b = True
                                        true_a = True
                                                                                        
                                        if rule.detect_r:
                                            if not eval(f"({r} {rule.r_operation} {rule.r_value})"):
                                                true_r = False
                                        
                                        if rule.detect_g:
                                            if not eval(f"({g} {rule.g_operation} {rule.g_value})"):
                                                true_g = False
                                        
                                        if rule.detect_b:
                                            if not eval(f"({b} {rule.b_operation} {rule.b_value})"):
                                                true_b = False
                                        
                                        if rule.detect_a:
                                            if not eval(f"({a} {rule.a_operation} {rule.a_value})"):
                                                true_a = False
                                                                                  
                                        if true_r and true_g and true_b and true_a:
                                            rgb_gate = True
                                else:
                                    rgb_gate = True
                                     
                                if rule.use_prop_detect:                                     
                                    prop_data_detect = {}
                                    for i in rule.prop_data_detect:
                                        prop_data_detect[i.prop_name] = [i.prop_value, i.prop_operation]
                                        
                                    if prop_data_detect:
                                        if original_principled:
                                            for input in original_principled.inputs:
                                                if input.name in prop_data_detect:
                                                
                                                    if eval(f"{input.default_value} {prop_data_detect[input.name][1]} {prop_data_detect[input.name][0]}"):
                                                        prop_detect_gate = True
                                else:
                                    prop_detect_gate = True                      
                                                                                                    
                                # Name Detect 
                                
                                if rule.use_name_detect:
                                    for n in name_list:

                                        if n.lower().strip() in mat.name.lower().strip():                                    
                                            name_gate = True
                                else:
                                    name_gate = True
                                
                                # Condition management
                                
                                and_list = []
                                or_list = []
                                
                                # Checking each condition
                                if rule.use_name_detect:
                                    if rule.name_detect_operation == "and":
                                        and_list.append(name_gate)
                                    else:
                                        or_list.append(name_gate)
                                
                                if rule.use_rgb_detect:
                                    if rule.rgb_operation == "and":
                                        and_list.append(rgb_gate)
                                    else:
                                        or_list.append(rgb_gate)
                                
                                if rule.use_prop_detect:
                                    if rule.prop_detect_operation == "and":
                                        and_list.append(prop_detect_gate)
                                    else:
                                        or_list.append(prop_detect_gate)
                                
                                and_condition = True                              
                                or_condition = False
                                
                                # When a list is empty, the condition results in False, appending a True in the empty list solves the problem
                                if len(and_list) == 0:
                                    and_list.append(True)
                                if len(or_list) == 0:
                                    or_list.append(True)
                                                                 
                                for condition in or_list:                                   
                                    if condition:
                                        or_condition = True
                                                                  
                                for condition in and_list:
                                    if not condition:
                                        and_condition = False
                                
                                if (and_condition and or_condition):                               
                                    detected_rule = rule
                                    material_detected = True
                                                                
                        if not material_detected:
                            #print('Material Not Detected')
                            continue
                        
                        if not detected_rule:
                            #print('Rule Not Detected')
                            continue
                        
                        if detected_rule.preset_to_activate == "NONE":
                            print('Rule has an empty preset')
                            continue
                        
                        #--------------------------------------------------
                        # Smart Pre-Setup Start
                        #--------------------------------------------------
                        
                        print(f'{detected_rule.smart_preset_name} Detected - {mat.name}')
                        
                        active_use_nodes(mat)                        
                        get_principled_nodes = [n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED']
                        
                        if not get_principled_nodes:
                            continue
                        
                        main_principled = get_principled_nodes[0]                      
                        reset_principled_node(main_principled)
                        
                        #--------------------------------------------------
                        # Smart Setup Start
                        #--------------------------------------------------
    
                        activate_selected_preset(self, context, detected_rule.preset_to_activate, main_principled, load_mode = 'DIRECT')
                        
                        #--------------------------------------------------
                        # Node Setup
                        #--------------------------------------------------
                        
                        if not detected_rule.select_node_setup == "NONE":
                            if detected_rule.select_node_setup == "BUMP_SETUP":                               
                                create_quick_bump(main_principled)
                                
                            
                            if detected_rule.select_node_setup == "TRANSLUCENT_SETUP":                               
                                create_quick_translucent(main_principled)
                        
                        #--------------------------------------------------
                        # Finishing operator
                        #--------------------------------------------------
                        
                        # Adding material that has settings changed by SMS, so that the operator does not run again in this material
                        new_mat = props.sms_ignore_materials.add()
                        new_mat.material_data = mat
                        
                        
                          
        return {'FINISHED'}   

    def invoke(self, context, event):
        
        default_x = event.mouse_x
        default_y = event.mouse_y
        
        generate_smart_preset_data()
        
        if self.rule_settings:
            
            props = bpy.context.scene.principledtools
            props.toggle_preset_edit = False
            
            context.window.cursor_warp(default_x - 205, default_y - 30)
            context.window_manager.invoke_popup(self, width=512)
            context.window.cursor_warp(default_x, default_y)

        else:
            self.smart_material_setup(context)
            
        return {'RUNNING_MODAL'}

    def execute(self, context):
        
        self.smart_material_setup()
        
        self.report({'INFO'},"Finished")
        return {'FINISHED'}

    def draw(self, context):
    
        layout = self.layout       
        draw_smart_mat_presets_ui(self,layout)

class PT_OP_AddSmartMatSetupJSON(bpy.types.Operator):
    """Add Smart Material Setup Data"""

    bl_idname = "pt.addsms"
    bl_label = "Update Data"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    rule_name : bpy.props.StringProperty(name='Smart Preset Name')
    #name_string : bpy.props.StringProperty(name='Material String')
    preset_to_activate : bpy.props.EnumProperty(name= "Preset", items=update_preset_enum_prop)
    
    def invoke(self, context, event):
        
        context.window_manager.invoke_props_dialog(self, width=420)
        
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        
        props = bpy.context.scene.principledtools
        props.sms_custom_index += 1
        
        new_s_preset = props.smart_material_setup_presets.add()
        new_s_preset.smart_preset_name = self.rule_name
        #new_s_preset.material_string = self.name_string
        new_s_preset.preset_to_activate = self.preset_to_activate
        
        write_smart_mat_json(self,context)
            
        return {'FINISHED'}   

    def draw(self, context):

        layout = self.layout       
        
        row = layout.row()
        row.prop(self,'rule_name')
        #row = layout.row()
        #row.prop(self,'name_string')
        row = layout.row()
        row.prop(self,'preset_to_activate')

class PT_OP_RemoveSmartMatSetupJSON(bpy.types.Operator):
    """Remove Smart Material Setup Data"""

    bl_idname = "pt.removesms"
    bl_label = "Update Data"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    rule_name : bpy.props.StringProperty(name='Smart Preset Name')
        
    def execute(self, context):
        
        props = bpy.context.scene.principledtools
        
        if props.sms_custom_index >= len(props.smart_material_setup_presets) - 1:
            props.sms_custom_index = len(props.smart_material_setup_presets) - 2
        
        idx = -1
        for p in props.smart_material_setup_presets:
            idx += 1
            if p.smart_preset_name == self.rule_name:
                props.smart_material_setup_presets.remove(idx)
               
        write_smart_mat_json(self,context)
            
        return {'FINISHED'}   
             
class PT_OP_MoveSmartMatSetupJSON(bpy.types.Operator):
    """Move Active Item"""

    bl_idname = "pt.moveitemsms"
    bl_label = "Move Item"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    move: bpy.props.EnumProperty(
        name= 'Move Item',
        default = 'UP',
        items = [
            ('UP','Up', ''),
            ('DOWN','Down', ''),
        ]        
    )
    
    def execute(self, context):
        
        props = bpy.context.scene.principledtools
        
        idx = props.sms_custom_index

        if self.move == 'UP':
            
            if not props.sms_custom_index == 0:
            
                props.smart_material_setup_presets.move(idx, idx-1)
                props.sms_custom_index -= 1
        
        if self.move == 'DOWN':
            
            if not props.sms_custom_index == len(props.smart_material_setup_presets) - 1:
            
                props.smart_material_setup_presets.move(idx, idx+1)
                props.sms_custom_index += 1
            
        write_smart_mat_json(self,context)
                      
        return {'FINISHED'}   

class PT_OP_ManagePropDetectSmartMatSetupJSON(bpy.types.Operator):
    """Manage Prop Detect System"""

    bl_idname = "pt.managepropdetect"
    bl_label = "Manage Prop Detect System"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    action: bpy.props.EnumProperty(
        name= 'Manage Item',
        default = 'ADD',
        items = [
            ('REMOVE','REMOVE', ''),
            ('ADD','ADD', ''),
            ('UP','Up', ''),
            ('DOWN','Down', ''),
        ]        
    )
    
    smart_preset_name : bpy.props.StringProperty()
    add_preset : bpy.props.StringProperty()
        
    def execute(self, context):
        
        props = bpy.context.scene.principledtools
        
        smart_preset = None
        smart_preset_idx = -1
        
        # Get Smart Preset Object
        if self.smart_preset_name:
                                
            for i in props.smart_material_setup_presets:
                smart_preset_idx += 1
                if i.smart_preset_name == self.smart_preset_name:
                    smart_preset = i
                    break
                
        if self.action == 'ADD':
            
            # Check Duplicate
            
            for p in smart_preset.prop_data_detect:
                if p.prop_name == self.add_preset:
                    
                    self.report({'WARNING'},"Property Already added")
                    return {'CANCELLED'}
            
            new_prop_detect = smart_preset.prop_data_detect.add()
            new_prop_detect.prop_name = self.add_preset
            new_prop_detect.prop_value = 1
            new_prop_detect.prop_operation = "=="
        
        if self.action == 'REMOVE':         
            smart_preset.prop_data_detect.remove(smart_preset_idx)
              
        write_smart_mat_json(self,context)
                      
        return {'FINISHED'}   

class PT_OP_ManageIgnoredSMSMaterials(bpy.types.Operator):
    """Refresh SMS stored Materials list"""

    bl_idname = "pt.manageignoredmaterials"
    bl_label = "Refresh SMS"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    action: bpy.props.EnumProperty(
        name= 'Manage',
        default = 'REMOVE',
        items = [
            ('REMOVE','Remove', ''),
        ]        
    )
    
    def execute(self, context):
          
        props = bpy.context.scene.principledtools
        
        if self.action == 'REMOVE':           
            print("Cleaning Materials")
            
            props.sms_ignore_materials.clear()
                                           
        return {'FINISHED'}   