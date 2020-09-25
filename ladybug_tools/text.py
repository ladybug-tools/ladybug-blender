"""Functions to add text to the Rhino scene and create Grasshopper text objects."""
import math

def text_objects(text, plane, height, font='Arial',
                 horizontal_alignment=0, vertical_alignment=5):
    """Generate a Bake-able Grasshopper text object from a text string and ladybug Plane.

    Args:
        text: A text string to be converted to a a Grasshopper text object.
        plane: A Ladybug Plane object to locate and orient the text in the Rhino scene.
        height: A number for the height of the text in the Rhino scene.
        font: An optional text string for the font in which to draw the text.
        horizontal_alignment: An optional integer to specify the horizontal alignment
             of the text. Choose from: (0 = Left, 1 = Center, 2 = Right)
        vertical_alignment: An optional integer to specify the vertical alignment
             of the text. Choose from: (0 = Top, 1 = MiddleOfTop, 2 = BottomOfTop,
             3 = Middle, 4 = MiddleOfBottom, 5 = Bottom, 6 = BottomOfBoundingBox)
    """
    # There is no standardised way to transfer text in Sverchok
    return LadybugText(text, plane, height, horizontal_alignment, vertical_alignment)


class LadybugText():
    def __init__(self, text, plane, height, horizontal_alignment, vertical_alignment):
        self.text = text
        self.plane = plane
        self.height = height
        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment
