import bpy

# Create Quick bump setup from principled 
def create_quick_bump(principled_node):
    
    node_tree = principled_node.id_data
    
    linked_node = None
    if principled_node.inputs['Base Color'].links:
        linked_node = principled_node.inputs['Base Color'].links[0].from_node
                                                                    
    #if linked_node and linked_node.type == 'TEX_IMAGE':   
    if linked_node:

        if principled_node.inputs['Normal'].links:
            return             
        
        text_node = linked_node 
                                                                                                                                                                                
        text_node_pos_x = text_node.location[0]
        text_node_pos_y = text_node.location[1]
        
        color_ramp = node_tree.nodes.new('ShaderNodeValToRGB')
        
        color_ramp.location[0] = text_node_pos_x
        color_ramp.location[1] = text_node_pos_y - 265
        color_ramp.hide = True
        
        bump_node = node_tree.nodes.new('ShaderNodeBump')
        bump_node.location = principled_node.location[0] - 150, principled_node.location[1] - 530
        bump_node.hide = True
        
        bump_node.inputs['Strength'].default_value = 0.1
        bump_node.inputs['Distance'].default_value = 0.01
        
        link = node_tree.links.new
        link(color_ramp.inputs[0],text_node.outputs[0])
        link(bump_node.inputs['Height'],color_ramp.outputs[0])
        link(principled_node.inputs['Normal'],bump_node.outputs[0])


def create_quick_translucent(principled_node):
    
    def create_nodes(node_tree,principled,out_put):
    
            mix_shader = node_tree.nodes.new('ShaderNodeMixShader')
                                        
            mix_shader.location[0] = principled.location[0] + 500
            mix_shader.location[1] = principled.location[1]                               

            translucent_shader = node_tree.nodes.new('ShaderNodeBsdfTranslucent')

            translucent_shader.location[0] = mix_shader.location[0] - 180
            translucent_shader.location[1] = mix_shader.location[1] - 120 
                                    
            mix_shader_2 = node_tree.nodes.new('ShaderNodeMixShader')
            mix_shader_2.location[0] = mix_shader.location[0] + 400
            mix_shader_2.location[1] = mix_shader.location[1]

            out_put.location[0] = mix_shader_2.location[0] + 300

            transparent_shader = node_tree.nodes.new('ShaderNodeBsdfTransparent')
            transparent_shader.location[0] = mix_shader_2.location[0] - 180
            transparent_shader.location[1] = mix_shader_2.location[1] - 120
            
            return mix_shader, translucent_shader, mix_shader_2, transparent_shader

    def default_links(link,mix_shader,mix_shader_2,translucent_shader,transparent_shader,out_put,principled):
        
        link(mix_shader.inputs[1],translucent_shader.outputs[0])
        link(mix_shader.inputs[2],principled.outputs[0])
        
        link(mix_shader_2.inputs[2],mix_shader.outputs[0])
        link(mix_shader_2.inputs[1],transparent_shader.outputs[0])
        
        link(out_put.inputs[0],mix_shader_2.outputs[0])
    
    node_tree = principled_node.id_data
    
    linked_node = None
    if principled_node.inputs['Base Color'].links:
        linked_node = principled_node.inputs['Base Color'].links[0].from_node
                                                                    
    #if linked_node and linked_node.type == 'TEX_IMAGE':
    if linked_node:  
        
        text_node = linked_node 
        
        if text_node.outputs['Color'].links:
            if text_node.outputs['Color'].links[0].to_node.type == 'BSDF_PRINCIPLED':
                                
                principled = text_node.outputs['Color'].links[0].to_node
                
                if principled.inputs['Alpha'].links:
                    remove_link = principled.inputs['Alpha'].links[0]                            
                    node_tree.links.remove(remove_link)                                         
                
                if principled.outputs[0].links:
                    if principled.outputs[0].links[0].to_node.type == 'OUTPUT_MATERIAL':
                        
                        out_put = principled.outputs[0].links[0].to_node
                                                                                                            
                        mix_shader, translucent_shader, mix_shader_2, transparent_shader = create_nodes(node_tree,principled,out_put)
                                                        
                        link = node_tree.links.new
                        
                        link(translucent_shader.inputs[0],text_node.outputs[0])
                        link(mix_shader_2.inputs[0],text_node.outputs[1])
                                                                                
                        default_links(link,mix_shader,mix_shader_2,translucent_shader,transparent_shader,out_put,principled)
 
    
class PT_OP_QuickBump(bpy.types.Operator): # change material props from mp 
    """Add Quick Bump to selected material"""

    bl_idname = "pt.quickbump"
    bl_label = "Quick Bump"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.active_object:
            return True

    def execute(self, context):

        objs = bpy.context.selected_objects

        for obj in objs:

            if hasattr(obj,'active_material'):
                mat = obj.active_material
                
                if mat.use_nodes:        
                    if hasattr(mat.node_tree.nodes,'active'):
                        
                        node_tree = mat.node_tree

                        principled_node = [n for n in node_tree.nodes if n.type == 'BSDF_PRINCIPLED']

                        if not principled_node:
                            continue
                        else:
                            principled_node = principled_node[0]

                        create_quick_bump(principled_node)
        
        self.report({'INFO'},"Quick Bump Done") 
        return {'FINISHED'}

class PT_OP_QuickTranslucent(bpy.types.Operator): # change material props from mp 
    """Add Quick Translucent to selected material"""

    bl_idname = "pt.quicktranslucent"
    bl_label = "Quick Translucent"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.active_object:
            return True

    def execute(self, context):
            
        for obj in bpy.context.selected_objects:

            if hasattr(obj,'active_material'):
                mat = obj.active_material
                
                if mat.use_nodes:        
                    if hasattr(mat.node_tree.nodes,'active'):
                        
                        node_tree = mat.node_tree

                        principled_node = [n for n in node_tree.nodes if n.type == 'BSDF_PRINCIPLED']

                        if not principled_node:
                            continue
                        else:
                            principled_node = principled_node[0]

                        create_quick_translucent(principled_node)
            
        self.report({'INFO'},"Quick Translucent Done")                                
        return {'FINISHED'}
