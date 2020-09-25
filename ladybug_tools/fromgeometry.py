"""Functions to translate from Ladybug geomtries to Rhino geometries."""
from .config import tolerance
#from .color import color_to_color, gray

"""____________2D GEOMETRY TRANSLATORS____________"""


def from_vector2d(vector):
    """Rhino Vector3d from ladybug Vector2D."""
    return vector
    return (vector.x, vector.y, 0)


def from_point2d(point, z=0):
    """Rhino Point3d from ladybug Point2D."""
    return point
    return (point.x, point.y, z)


def from_ray2d(ray, z=0):
    """Rhino Ray3d from ladybug Ray2D."""
    return ray
    return rg.Ray3d(from_point2d(ray.p, z), from_vector2d(ray.v))


def from_linesegment2d(line, z=0):
    """Rhino LineCurve from ladybug LineSegment2D."""
    return line


def from_arc2d(arc, z=0):
    """Rhino Arc from ladybug Arc2D."""
    return arc


def from_polygon2d(polygon, z=0):
    """Rhino closed PolyLineCurve from ladybug Polygon2D."""
    return polygon


def from_polyline2d(polyline, z=0):
    """Rhino closed PolyLineCurve from ladybug Polyline2D."""
    return polyline


def from_mesh2d(mesh, z=0):
    """Rhino Mesh from ladybug Mesh2D."""
    return mesh


"""____________3D GEOMETRY TRANSLATORS____________"""


def from_vector3d(vector):
    """Rhino Vector3d from ladybug Vector3D."""
    return vector


def from_point3d(point):
    """Rhino Point3d from ladybug Point3D."""
    return point


def from_ray3d(ray, z=0):
    """Rhino Ray3d from ladybug Ray3D."""
    return ray


def from_linesegment3d(line):
    """Rhino LineCurve from ladybug LineSegment3D."""
    return line


def from_plane(pl):
    """Rhino Plane from ladybug Plane."""
    return pl


def from_arc3d(arc):
    """Rhino Arc from ladybug Arc3D."""
    return arc


def from_polyline3d(polyline):
    """Rhino closed PolyLineCurve from ladybug Polyline3D."""
    return polyline


def from_mesh3d(mesh):
    """Rhino Mesh from ladybug Mesh3D."""
    return mesh


def from_face3d(face):
    """Rhino Brep from ladybug Face3D."""
    return face


def from_polyface3d(polyface):
    """Rhino Brep from ladybug Polyface3D."""
    return polyface


"""________ADDITIONAL 3D GEOMETRY TRANSLATORS________"""


def from_face3d_to_wireframe(face):
    """Rhino PolyLineCurve from ladybug Face3D."""
    return face


def from_polyface3d_to_wireframe(polyface):
    """Rhino PolyLineCurve from ladybug Polyface3D."""
    return polyface


def from_face3d_to_solid(face, offset):
    """Rhino Solid Brep from a ladybug Face3D and an offset."""
    return "TODO FROM FACE3D TO SOLID"
    srf_brep = from_face3d(face)
    return rg.Brep.CreateFromOffsetFace(
        srf_brep.Faces[0], offset, tolerance, False, True)


def from_face3ds_to_colored_mesh(faces, color):
    """Colored Rhino mesh from an array of ladybug Face3D and ladybug Color.

    This is used in workflows such as coloring Model geomtry with results.
    """
    return "TODO FACE3D TO COLORED MESH"
    joined_mesh = rg.Mesh()
    for face in faces:
        try:
            joined_mesh.Append(rg.Mesh.CreateFromBrep(
                from_face3d(face), rg.MeshingParameters.Default)[0])
        except TypeError:
            pass  # failed to create a Rhino Mesh from the Face3D
    joined_mesh.VertexColors.CreateMonotoneMesh(color_to_color(color))
    return joined_mesh
