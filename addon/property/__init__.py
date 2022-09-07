import bpy

from .addon_props import PT_Addon_Props
from .collection_props import PT_SmartMaterialSetupPresets, PT_PresetsCollection, PT_PresetPropData, PT_SMSPropData, PT_SmartMaterialSetupsIgnoreMaterials
from .addon_preferences import PT_AddonPrefs

classes = (
    PT_SmartMaterialSetupsIgnoreMaterials, PT_SMSPropData, PT_PresetPropData, PT_PresetsCollection, PT_SmartMaterialSetupPresets, PT_Addon_Props, PT_AddonPrefs
)

def register_addon_properties():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.principledtools = bpy.props.PointerProperty(type= PT_Addon_Props)

def unregister_addon_properties():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.principledtools