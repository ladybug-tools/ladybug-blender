"""Functions to create Ladybug geometries from Rhino geometries."""

import bpy
import mathutils

try:
    from ladybug_geometry.geometry2d.pointvector import Vector2D, Point2D
    from ladybug_geometry.geometry2d.ray import Ray2D
    from ladybug_geometry.geometry2d.line import LineSegment2D
    from ladybug_geometry.geometry2d.polygon import Polygon2D
    from ladybug_geometry.geometry2d.mesh import Mesh2D
    from ladybug_geometry.geometry3d.pointvector import Vector3D, Point3D
    from ladybug_geometry.geometry3d.ray import Ray3D
    from ladybug_geometry.geometry3d.line import LineSegment3D
    from ladybug_geometry.geometry3d.plane import Plane
    from ladybug_geometry.geometry3d.mesh import Mesh3D
    from ladybug_geometry.geometry3d.face import Face3D
    from ladybug_geometry.geometry3d.polyface import Polyface3D
except ImportError as e:
    raise ImportError(
        "Failed to import ladybug_geometry.\n{}".format(e))
try:
    import ladybug.color as lbc
except ImportError as e:
    raise ImportError("Failed to import ladybug.\n{}".format(e))

#import ladybug_rhino.planarize as _planar
#from .config import tolerance


"""____________2D GEOMETRY TRANSLATORS____________"""


def to_vector2d(vector):
    """Ladybug Vector2D from Rhino Vector3d."""
    if isinstance(vector, Vector2D):
        return vector
    elif isinstance(vector, (list, tuple)):
        return Vector2D(vector[0], vector[1])


def to_point2d(point):
    """Ladybug Point2D from Rhino Point3d."""
    if isinstance(point, Point3D):
        return Point2D(point.x, point.y)
    elif isinstance(point, Point2D):
        return point
    elif isinstance(point, (list, tuple)):
        return Point2D(point[0], point[1])


def to_ray2d(ray):
    """Ladybug Ray2D from Rhino Ray3d."""
    return ray


def to_linesegment2d(line):
    """Ladybug LineSegment2D from Rhino LineCurve."""
    return line


def to_polygon2d(polygon):
    """Ladybug Polygon2D from Rhino closed PolyLineCurve."""
    return polygon


def to_mesh2d(mesh, color_by_face=True):
    """Ladybug Mesh2D from Rhino Mesh."""
    return mesh


"""____________3D GEOMETRY TRANSLATORS____________"""


def to_vector3d(vector):
    """Ladybug Vector3D from Rhino Vector3d."""
    return vector


def to_point3d(point):
    """Ladybug Point3D from Rhino Point3d."""
    if isinstance(point, Point3D):
        return point
    elif isinstance(point, (list, tuple, mathutils.Vector)):
        return Point3D(point[0], point[1], point[2])
    elif isinstance(point, bpy.types.MeshVertex):
        return Point3D(point.co[0], point.co[1], point.co[2])


def to_ray3d(ray):
    """Ladybug Ray3D from Rhino Ray3d."""
    return ray


def to_linesegment3d(line):
    """Ladybug LineSegment3D from Rhino LineCurve."""
    return line


def to_plane(pl):
    """Ladybug Plane from Rhino Plane."""
    return pl


def to_face3d(geo, meshing_parameters=None):
    """List of Ladybug Face3D objects from a Rhino Brep, Surface or Mesh.

    Args:
        brep: A Rhino Brep, Surface or Mesh that will be converted into a list
            of Ladybug Face3D.
        meshing_parameters: Optional Rhino Meshing Parameters to describe how
            curved faces should be converted into planar elements. If None,
            Rhino's Default Meshing Parameters will be used.
    """
    return geo


def to_polyface3d(geo, meshing_parameters=None):
    """A Ladybug Polyface3D object from a Rhino Brep.

    Args:
        geo: A Rhino Brep, Surface ro Mesh that will be converted into a single
            Ladybug Polyface3D.
        meshing_parameters: Optional Rhino Meshing Parameters to describe how
            curved faces should be converted into planar elements. If None,
            Rhino's Default Meshing Parameters will be used.
    """
    return geo


def to_mesh3d(mesh, color_by_face=True):
    """Ladybug Mesh3D from Rhino Mesh."""
    if isinstance(mesh, Mesh3D):
        return mesh
    elif isinstance(mesh, bpy.types.Object):
        lb_verts = tuple(to_point3d(mesh.matrix_world @ pt.co) for pt in mesh.data.vertices)
        lb_faces, colors = _extract_mesh_faces_colors(mesh, mesh.data, color_by_face)
        return Mesh3D(lb_verts, lb_faces, colors)


"""________ADDITIONAL 3D GEOMETRY TRANSLATORS________"""


def to_gridded_mesh3d(brep, grid_size, offset_distance=0):
    """Create a gridded Ladybug Mesh3D from a Rhino Brep.

    This is useful since Rhino's grid meshing is often more beautiful than what
    ladybug_geometry can produce. However, the ladybug_geometry Face3D.get_mesh_grid
    method provides a workable alternative to this if it is needed.

    Args:
        brep: A Rhino Brep that will be converted into a gridded Ladybug Mesh3D.
        grid_size: A number for the grid size dimension with which to make the mesh.
        offset_distance: A number for the distance at which to offset the mesh from
            the underlying brep. The default is 0.
    """
    # For now, let blender handle gridding via subdiv modifier
    new_data = bpy.data.meshes.new_from_object(brep.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    new_data.transform(brep.matrix_world)
    new = bpy.data.objects.new('Evaluated Object', new_data)
    for vertex in new.data.vertices:
        vertex.co = vertex.co + (vertex.normal * offset_distance)
    return to_mesh3d(new)


def to_joined_gridded_mesh3d(geometry, grid_size, offset_distance=0):
    """Create a single gridded Ladybug Mesh3D from an array of Rhino geometry.

    Args:
        breps: An array of Rhino Breps and/or Rhino meshes that will be converted
            into a single, joined gridded Ladybug Mesh3D.
        grid_size: A number for the grid size dimension with which to make the mesh.
        offset_distance: A number for the distance at which to offset the mesh from
            the underlying brep. The default is 0.
    """
    lb_meshes = []
    for geo in geometry:
        if isinstance(geo, bpy.types.Object):
            lb_meshes.append(to_gridded_mesh3d(geo, grid_size, offset_distance))
        else:  # assume that it's a Mesh
            lb_meshes.append(to_mesh3d(geo))
    if len(lb_meshes) == 1:
        return lb_meshes[0]
    else:
        return Mesh3D.join_meshes(lb_meshes)


"""________________EXTRA HELPER FUNCTIONS________________"""


def _extract_mesh_faces_colors(obj, mesh, color_by_face):
    """Extract face indices and colors from a Rhino mesh."""
    colors = None
    lb_faces = []
    colors = []
    for face in mesh.polygons:
        # TODO: does LB handle ngons?
        lb_faces.append(tuple(face.vertices))
        if obj.material_slots:
            c = obj.material_slots[face.material_index].material.diffuse_color
            colors.append(lbc.Color(int(c[0]*255), int(c[1]*255), int(c[2]*255)))
        else:
            colors.append(lbc.Color(0, 0, 0))
    return lb_faces, colors
