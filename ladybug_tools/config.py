"""Ladybug_rhino configurations.
Global variables such as tolerances and units are stored here.
"""

# I didn't see where Blender does tolerance, until I do, let's copy Rhino
# TODO: check where this is used, if at all. If not, remove.
tolerance = 0.01
angle_tolerance = 1.0  # default is 1 degree


def conversion_to_meters():
    """Get the conversion factor to meters based on the current Rhino doc units system.
    Returns:
        A number for the conversion factor, which should be multiplied by all distance
        units taken from Rhino geometry in order to convert them to meters.
    """
    # Blender (and Sverchok) always works in meters internally
    return 1.0


def units_system():
    """Get text for the current Rhino doc units system. (eg. 'Meters', 'Feet')"""
    return "TODO"


def units_abbreviation():
    """Get text for the current Rhino doc units abbreviation (eg. 'm', 'ft')"""
    return "TODO"
