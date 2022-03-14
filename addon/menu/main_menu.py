import bpy

from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList,
                       Menu)
        
class PT_PT_Pie_MainPie(Menu):

    bl_idname = 'pt.maintools'
    bl_label = "Principled Tools"

    def draw(self, context):

        # Draw Start -----------------------

        layout = self.layout

        pie = layout.menu_pie()
        other = pie.column(align=True)
        gap = other.column()

        #gap.scale_x = 1
        libray_menu = other.box().column()
        libray_menu.scale_y= 1
        libray_menu.scale_x=1

        # operator_enum will just spread all available options
        # for the type enum of the operator on the pie

        libray_menu.label(text='MP Fast Material Library')

        gap = other.column()
        gap = other.column()
        
        counter_ml = 0

        test = 10
 
        for m in range(10):
            libray_menu = other.column(align=True)
            libray_menu.scale_y= 1
            libray_menu.scale_x=1.2
            counter_ml +=1

            libray_menu.operator("mp.selectmaterial")

  
                  

