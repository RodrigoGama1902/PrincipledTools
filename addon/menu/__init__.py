import bpy


from .main_menu import PT_PT_Pie_MainPie



classes = (
    PT_PT_Pie_MainPie,
)


def register_menus():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister_menus():
    
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)