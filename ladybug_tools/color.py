"""Collection of methods for converting between Ladybug and .NET colors."""

from ladybug.color import Color

def color_to_color(color, alpha=255):
    """Convert a ladybug color into .NET color.

    Args:
        alpha: Optional integer betwen 1 and 255 for the alpha value of the color.
    """
    return color
    try:
        return Color.FromArgb(alpha, color.r, color.g, color.b)
    except AttributeError as e:
        raise AttributeError('Input must be of type of Color:\n{}'.format(e))


def gray():
    """Get a .NET gray color object. Useful when you need a placeholder color."""
    return Color(90, 90, 90, 255)


def black():
    """Get a .NET black color object. Useful for things like default text."""
    return Color(0, 0, 0, 255)
    return Color.Black
