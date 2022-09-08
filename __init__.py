
bl_info = {
    "name": "Principled Tools",
    "description": "A collection of tools that will help you speed up your Principled Shader pipeline",
    "author": "Rodrigo Gama",
    "version": (0, 5, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View"
}


def register():
    from .addon.register import register_addon
    register_addon()


def unregister():
    from .addon.register import unregister_addon
    unregister_addon()