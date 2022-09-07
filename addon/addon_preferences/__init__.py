from ..addon_preferences.addon_preferences import PT_AddonPrefs


classes = (
    PT_AddonPrefs,
)

def register_addon_preferences():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister_addon_preferences():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
