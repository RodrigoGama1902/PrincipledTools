import bpy

from .pricipled_tools import (PT_MainPrincipledTool,
                              PT_OP_CreateNewMaterial,
                              PT_OP_BaseColorSettings,
                              PT_OP_RemoveHelperNodes,
                              PT_OP_ExtraOptions,)

from .preset_system import (PT_PresetSystem,
                            PT_ActivatePreset,
                            PT_AddPPreset,
                            PT_RemovePreset,
                            PT_ActivateLastPreset
                            )

from .smart_material_setup_system import (
                            PT_OP_SmartMaterialSetup,
                            PT_OP_AddSmartMatSetupJSON,
                            PT_OP_RemoveSmartMatSetupJSON,
                            PT_SMS_UL_items,
                            PT_OP_MoveSmartMatSetupJSON,
                            PT_OP_ManagePropDetectSmartMatSetupJSON,
                            PT_OP_ManageIgnoredSMSMaterials
                            )

from .node_operators import (PT_OP_QuickBump,
                             PT_OP_QuickTranslucent)

classes = (
    PT_SMS_UL_items,
    PT_MainPrincipledTool,
    PT_PresetSystem,
    PT_ActivatePreset,
    PT_OP_QuickBump,
    PT_OP_QuickTranslucent,
    PT_OP_CreateNewMaterial,
    PT_OP_BaseColorSettings,
    PT_OP_RemoveHelperNodes,
    PT_OP_ExtraOptions,
    PT_OP_SmartMaterialSetup,
    PT_AddPPreset,
    PT_RemovePreset,
    PT_OP_AddSmartMatSetupJSON,
    PT_OP_RemoveSmartMatSetupJSON,
    PT_OP_MoveSmartMatSetupJSON,
    PT_OP_ManagePropDetectSmartMatSetupJSON,
    PT_OP_ManageIgnoredSMSMaterials,
    PT_ActivateLastPreset
)

def register_operators():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister_operators():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)