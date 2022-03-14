

def register_addon():

    # Operators
    from ..operator import register_operators
    register_operators()

    #from ..menu import register_menus
    #register_menus()

    from .keymap import register_keymap
    register_keymap()

    from ..property import register_addon_properties
    register_addon_properties()


def unregister_addon():

    # Operators
    from ..operator import unregister_operators
    unregister_operators()

    #from ..menu import unregister_menus
    #unregister_menus()

    from ..property import unregister_addon_properties
    unregister_addon_properties()

    from .keymap import unregister_keymap
    unregister_keymap()
