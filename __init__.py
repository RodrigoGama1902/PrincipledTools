import bpy

bl_info = {
    "name": "Principled Tool",
    "description": "Quick Ajusts for Principled Shader",
    "author": "Rodrigo Gama",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "View3D",
    "category": "3D View"
}


def register():
    from .addon.register import register_addon
    register_addon()


def unregister():
    from .addon.register import unregister_addon
    unregister_addon()