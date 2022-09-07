

def register_addon():

    from ..operator import register_operators
    register_operators()

    from .keymap import register_keymap
    register_keymap()
    
    from ..addon_preferences import register_addon_preferences
    register_addon_preferences()

    from ..property import register_addon_properties
    register_addon_properties()


def unregister_addon():

    from ..operator import unregister_operators
    unregister_operators()
    
    from ..addon_preferences import unregister_addon_preferences
    unregister_addon_preferences()

    from ..property import unregister_addon_properties
    unregister_addon_properties()

    from .keymap import unregister_keymap
    unregister_keymap()
