"""Classes for colorized versions of various Rhino objects like points."""
from .color import black

class ColoredPoint():
    """A Point object with a set-able color property to change its color in Grasshopper.

    Args:
        point: A Rhino Point3d object.
    """

    def __init__(self, point):
        """Initialize ColoredPoint."""
        self.point = point
        self.color = black()

    def DuplicateGeometry(self):
        point = rh.Geometry.Point3d(self.point.X, self.point.Y, self.point.Z)
        new_pt = ColoredPoint(point)
        new_pt.color = self.color
        return new_pt

    def get_TypeName(self):
        return "Colored Point"

    def get_TypeDescription(self):
        return "Colored Point"

    def ToString(self):
        return '{}, {}, {}'.format(self.color.R, self.color.G, self.color.B)

    def Transform(self, xform):
        point = rh.Geometry.Point3d(self.point.X, self.point.Y, self.point.Z)
        point.Transform(xform)
        new_pt = ColoredPoint(point)
        new_pt.color = self.color
        return new_pt

    def Morph(self, xmorph):
        return self.DuplicateGeometry()

    def DrawViewportWires(self, args):
        args.Pipeline.DrawPoint(self.point, rh.Display.PointStyle.RoundSimple, 5, self.color)

    def DrawViewportMeshes(self, args):
        # Do not draw in meshing layer.
        pass

    def BakeGeometry(self, doc, att, id):
        id = guid.Empty
        if att is None:
            att = doc.CreateDefaultAttributes()
        att.ColorSource = rh.DocObjects.ObjectColorSource.ColorFromObject
        att.ObjectColor = self.color
        id = doc.Objects.AddPoint(self.point, att)
        return True, id
