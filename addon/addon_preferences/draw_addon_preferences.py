

def draw_addon_preferences(self, context):

    layout = self.layout
    
    box = layout.box()
    box.label(text='Principled Tools')
    p_row = box.row()
    p_row.prop(self, "auto_new_material")
    
    box = layout.box()
    box.label(text='Smart Material Setup')
    p_row = box.row()
    p_row.prop(self, "store_materials_sms")
    
    box = layout.box()
    box.label(text='Extra Widgets')
    p_row = box.row()
    p_row.prop(self, "widget_new_material")
    
    box = layout.box()
    props_row = box.row()
    props_row.label(text='Active Principled Inputs')
    props_row.prop(self, "show_pi_props_in_prefs", text="", icon="TRIA_DOWN")
            
    if self.show_pi_props_in_prefs:        
        for p in self.__annotations__:
            if p.startswith('show_pi_'):
                if hasattr(self,p):
                    p_row = box.row()
                    p_row.active = getattr(self,p)
                    p_row.prop(self, p)