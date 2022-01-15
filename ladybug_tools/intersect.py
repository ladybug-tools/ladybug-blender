"""Functions to handle intersection of Rhino geometries.

These represent geometry computation methods  that are either not supported by
ladybug_geometry or there are much more efficient versions of them in Rhino.
"""
import bpy
import math
import types
import mathutils.geometry
import array as specializedarray
from .config import tolerance
from mathutils import Vector, Matrix


# Stub for .net tasks.

def for_each(iterable, fn):
    for i in iterable:
        fn(i)
    return # Does this work in Sverchok?

    pool = multiprocessing.Pool()
    pool.map(fn, iterable)
    pool.close()
    pool.join()

tasks = types.SimpleNamespace()
Parallel = types.SimpleNamespace()
Parallel.ForEach = for_each
tasks.Parallel = Parallel


def join_geometry_to_mesh(geometry):
    """Convert an array of Rhino Breps and/or Meshes into a single Rhino Mesh.

    This is a typical pre-step before using the intersect_mesh_rays function.

    Args:
        geometry: An array of Rhino Breps or Rhino Meshes.
    """
    copied_geometry = []
    for geo in geometry:
        new = geo.copy()
        new.data = new.data.copy()
        copied_geometry.append(new)
    c = {}
    c['object'] = c['active_object'] = copied_geometry[0]
    c['selected_objects'] = c['selected_editable_objects'] = copied_geometry
    bpy.ops.object.join(c)
    bpy.context.scene.collection.objects.link(copied_geometry[0])
    # Apply all transformations
    copied_geometry[0].data.transform(copied_geometry[0].matrix_world)
    copied_geometry[0].matrix_world = Matrix()
    return copied_geometry[0]
    for geo in geometry:
        if isinstance(geo, rg.Brep):
            meshes = rg.Mesh.CreateFromBrep(geo, rg.MeshingParameters.Default)
            for mesh in meshes:
                joined_mesh.Append(mesh)
        elif isinstance(geo, rg.Mesh):
            joined_mesh.Append(geo)
        else:
            raise TypeError('Geometry must be either a Brep or a Mesh. '
                            'Not {}.'.format(type(geo)))
    return joined_mesh


def intersect_mesh_rays(
        mesh, points, vectors, normals=None, cpu_count=None, parallel=True):
    """Intersect a group of rays (represented by points and vectors) with a mesh.

    All combinations of rays that are possible between the input points and
    vectors will be intersected. This method exists since most CAD plugins have
    much more efficient mesh/ray intersection functions than ladybug_geometry.
    However, the ladybug_geometry Face3D.intersect_line_ray() method provides
    a workable (albeit very inefficient) alternative to this if it is needed.

    Args:
        mesh: A Rhino mesh that can block the rays.
        points: An array of Rhino points that will be used to generate rays.
        vectors: An array of Rhino vectors that will be used to generate rays.
        normals: An optional array of Rhino vectors that align with the input
            points and denote the direction each point is facing. These will
            be used to eliminate any cases where the vector and the normal differ
            by more than 90 degrees. If None, points are assumed to have no direction.
        cpu_count: An integer for the number of CPUs to be used in the intersection
            calculation. The ladybug_rhino.grasshopper.recommended_processor_count
            function can be used to get a recommendation. If set to None, all
            available processors will be used. (Default: None).
        parallel: Optional boolean to override the cpu_count and use a single CPU
            instead of multiple processors.

    Returns:
        A tuple with two elements

        -   intersection_matrix -- A 2D matrix of 0's and 1's indicating the results
            of the intersection. Each sub-list of the matrix represents one of the
            points and has a length equal to the vectors. 0 indicates a blocked
            ray and 1 indicates a ray that was not blocked.

        -   angle_matrix -- A 2D matrix of angles in radians. Each sub-list of the
            matrix represents one of the normals and has a length equal to the
            supplied vectors. Will be None if no normals are provided.
    """
    intersection_matrix = [0] * len(points)  # matrix to be filled with results
    angle_matrix = [0] * len(normals) if normals is not None else None
    cutoff_angle = math.pi / 2  # constant used in all normal checks
    if not parallel:
        cpu_count = 1

    def intersect_point(i):
        """Intersect all of the vectors of a given point without any normal check."""
        pt = points[i]
        int_list = []
        for vec in vectors:
            is_clear = 0 if mesh.ray_cast(
                Vector((pt.x, pt.y, pt.z)),
                Vector((vec.x, vec.y, vec.z)))[0] else 1
            int_list.append(is_clear)
        intersection_matrix[i] = int_list

    def intersect_point_normal_check(i):
        """Intersect all of the vectors of a given point with a normal check."""
        pt, normal_vec = points[i], normals[i]
        int_list = []
        angle_list = []
        for vec in vectors:
            vec_angle = Vector((normal_vec.x, normal_vec.y, normal_vec.z)).angle(Vector((vec.x, vec.y, vec.z)))
            angle_list.append(vec_angle)
            if vec_angle <= cutoff_angle:
                is_clear = 0 if mesh.ray_cast(
                    Vector((pt.x, pt.y, pt.z)),
                    Vector((vec.x, vec.y, vec.z)))[0] else 1
                int_list.append(is_clear)
            else:  # the vector is pointing behind the surface
                int_list.append(0)
        intersection_matrix[i] = specializedarray.array('B', int_list)
        angle_matrix[i] = specializedarray.array('d', angle_list)

    def intersect_each_point_group(worker_i):
        """Intersect groups of points so that only the cpu_count is used."""
        start_i, stop_i = pt_groups[worker_i]
        for count in range(start_i, stop_i):
            intersect_point(count)

    def intersect_each_point_group_normal_check(worker_i):
        """Intersect groups of points with distance check so only cpu_count is used."""
        start_i, stop_i = pt_groups[worker_i]
        for count in range(start_i, stop_i):
            intersect_point_normal_check(count)

    if cpu_count is not None and cpu_count > 1:
        # group the points in order to meet the cpu_count
        pt_count = len(points)
        worker_count = min((cpu_count, pt_count))
        i_per_group = int(math.ceil(pt_count / worker_count))
        pt_groups = [[x, x + i_per_group] for x in range(0, pt_count, i_per_group)]
        pt_groups[-1][-1] = pt_count  # ensure the last group ends with point count

    if normals is not None:
        if cpu_count is None:  # use all availabe CPUs
            tasks.Parallel.ForEach(range(len(points)), intersect_point_normal_check)
        elif cpu_count <= 1:  # run everything on a single processor
            for i in range(len(points)):
                intersect_point_normal_check(i)
        else:  # run the groups in a manner that meets the CPU count
            tasks.Parallel.ForEach(
                range(len(pt_groups)), intersect_each_point_group_normal_check)
    else:
        if cpu_count is None:  # use all availabe CPUs
            tasks.Parallel.ForEach(range(len(points)), intersect_point)
        elif cpu_count <= 1:  # run everything on a single processor
            for i in range(len(points)):
                intersect_point(i)
        else:  # run the groups in a manner that meets the CPU count
            tasks.Parallel.ForEach(range(len(pt_groups)), intersect_each_point_group)

    return intersection_matrix, angle_matrix


def intersect_mesh_lines(
        mesh, start_points, end_points, max_dist=None, cpu_count=None, parallel=True):
    """Intersect a group of lines (represented by start + end points) with a mesh.

    All combinations of lines that are possible between the input start_points and
    end_points will be intersected. This method exists since most CAD plugins have
    much more efficient mesh/line intersection functions than ladybug_geometry.
    However, the ladybug_geometry Face3D.intersect_line_ray() method provides
    a workable (albeit very inefficient) alternative to this if it is needed.

    Args:
        mesh: A Rhino mesh that can block the lines.
        start_points: An array of Rhino points that will be used to generate lines.
        end_points: An array of Rhino points that will be used to generate lines.
        max_dist: An optional number to set the maximum distance beyond which the
            end_points are no longer considered visible by the start_points.
            If None, points with an unobstructed view to one another will be
            considered visible no matter how far they are from one another.
        cpu_count: An integer for the number of CPUs to be used in the intersection
            calculation. The ladybug_rhino.grasshopper.recommended_processor_count
            function can be used to get a recommendation. If set to None, all
            available processors will be used. (Default: None).
        parallel: Optional boolean to override the cpu_count and use a single CPU
            instead of multiple processors.

    Returns:
        A 2D matrix of 0's and 1's indicating the results of the intersection.
        Each sub-list of the matrix represents one of the points and has a
        length equal to the end_points. 0 indicates a blocked ray and 1 indicates
        a ray that was not blocked.
    """
    int_matrix = [0] * len(start_points)  # matrix to be filled with results
    if not parallel:
        cpu_count = 1

    def intersect_line(i):
        """Intersect a line defined by a start and an end with the mesh."""
        pt = start_points[i]
        int_list = []
        for ept in end_points:
            lin = rg.Line(pt, ept)
            int_obj = rg.Intersect.Intersection.MeshLine(mesh, lin)
            is_clear = 1 if None in int_obj or len(int_obj) == 0 else 0
            int_list.append(is_clear)
        int_matrix[i] = int_list

    def intersect_line_dist_check(i):
        """Intersect a line with the mesh with a distance check."""
        pt = start_points[i]
        int_list = []
        for ept in end_points:
            lin = rg.Line(pt, ept)
            if lin.Length > max_dist:
                int_list.append(0)
            else:
                int_obj = rg.Intersect.Intersection.MeshLine(mesh, lin)
                is_clear = 1 if None in int_obj or len(int_obj) == 0 else 0
                int_list.append(is_clear)
        int_matrix[i] = int_list

    def intersect_each_line_group(worker_i):
        """Intersect groups of lines so that only the cpu_count is used."""
        start_i, stop_i = l_groups[worker_i]
        for count in range(start_i, stop_i):
            intersect_line(count)

    def intersect_each_line_group_dist_check(worker_i):
        """Intersect groups of lines with distance check so only cpu_count is used."""
        start_i, stop_i = l_groups[worker_i]
        for count in range(start_i, stop_i):
            intersect_line_dist_check(count)

    if cpu_count is not None and cpu_count > 1:
        # group the lines in order to meet the cpu_count
        l_count = len(start_points)
        worker_count = min((cpu_count, l_count))
        i_per_group = int(math.ceil(l_count / worker_count))
        l_groups = [[x, x + i_per_group] for x in range(0, l_count, i_per_group)]
        l_groups[-1][-1] = l_count  # ensure the last group ends with line count

    if max_dist is not None:
        if cpu_count is None:  # use all availabe CPUs
            tasks.Parallel.ForEach(range(len(start_points)), intersect_line_dist_check)
        elif cpu_count <= 1:  # run everything on a single processor
            for i in range(len(start_points)):
                intersect_line_dist_check(i)
        else:  # run the groups in a manner that meets the CPU count
            tasks.Parallel.ForEach(
                range(len(l_groups)), intersect_each_line_group_dist_check)
    else:
        if cpu_count is None:  # use all availabe CPUs
            tasks.Parallel.ForEach(range(len(start_points)), intersect_line)
        elif cpu_count <= 1:  # run everything on a single processor
            for i in range(len(start_points)):
                intersect_line(i)
        else:  # run the groups in a manner that meets the CPU count
            tasks.Parallel.ForEach(
                range(len(l_groups)), intersect_each_line_group)
    return int_matrix


def intersect_solids_parallel(solids, bound_boxes, cpu_count=None):
    """Intersect the co-planar faces of an array of solids using parallel processing.

    Args:
        original_solids: An array of closed Rhino breps (polysurfaces) that do
            not have perfectly matching surfaces between adjacent Faces.
        bound_boxes: An array of Rhino bounding boxes that parellels the input
            solids and will be used to check whether two Breps have any potential
            for intersection before the actual intersection is performed.
        cpu_count: An integer for the number of CPUs to be used in the intersection
            calculation. The ladybug_rhino.grasshopper.recommended_processor_count
            function can be used to get a recommendation. If None, all available
            processors will be used. (Default: None).
        parallel: Optional boolean to override the cpu_count and use a single CPU
            instead of multiple processors.

    Returns:
        int_solids -- The input array of solids, which have all been intersected
        with one another.
    """
    int_solids = solids[:]  # copy the input list to avoid editing it

    def intersect_each_solid(i):
        """Intersect a solid with all of the other solids of the list."""
        bb_1 = bound_boxes[i]
        # intersect the solids that come after this one
        for j, bb_2 in enumerate(bound_boxes[i + 1:]):
            if not overlapping_bounding_boxes(bb_1, bb_2):
                continue  # no overlap in bounding box; intersection impossible
            split_brep1, int_exists = \
                intersect_solid(int_solids[i], int_solids[i + j + 1])
            if int_exists:
                int_solids[i] = split_brep1
        # intersect the solids that come before this one
        for j, bb_2 in enumerate(bound_boxes[:i]):
            if not overlapping_bounding_boxes(bb_1, bb_2):
                continue  # no overlap in bounding box; intersection impossible
            split_brep2, int_exists = intersect_solid(int_solids[i], int_solids[j])
            if int_exists:
                int_solids[i] = split_brep2

    def intersect_each_solid_group(worker_i):
        """Intersect groups of solids so that only the cpu_count is used."""
        start_i, stop_i = s_groups[worker_i]
        for count in range(start_i, stop_i):
            intersect_each_solid(count)

    if cpu_count is None or cpu_count <= 1:  # use all availabe CPUs
        tasks.Parallel.ForEach(range(len(solids)), intersect_each_solid)
    else:  # group the solids in order to meet the cpu_count
        solid_count = len(int_solids)
        worker_count = min((cpu_count, solid_count))
        i_per_group = int(math.ceil(solid_count / worker_count))
        s_groups = [[x, x + i_per_group] for x in range(0, solid_count, i_per_group)]
        s_groups[-1][-1] = solid_count  # ensure the last group ends with solid count
        tasks.Parallel.ForEach(range(len(s_groups)), intersect_each_solid_group)

    return int_solids


def intersect_solids(solids, bound_boxes):
    """Intersect the co-planar faces of an array of solids.

    Args:
        original_solids: An array of closed Rhino breps (polysurfaces) that do
            not have perfectly matching surfaces between adjacent Faces.
        bound_boxes: An array of Rhino bounding boxes that parellels the input
            solids and will be used to check whether two Breps have any potential
            for intersection before the actual intersection is performed.

    Returns:
        int_solids -- The input array of solids, which have all been intersected
        with one another.
    """
    int_solids = solids[:]  # copy the input list to avoid editing it

    for i, bb_1 in enumerate(bound_boxes):
        for j, bb_2 in enumerate(bound_boxes[i + 1:]):
            if not overlapping_bounding_boxes(bb_1, bb_2):
                continue  # no overlap in bounding box; intersection impossible

            # split the first solid with the second one
            split_brep1, int_exists = intersect_solid(
                int_solids[i], int_solids[i + j + 1])
            int_solids[i] = split_brep1

            # split the second solid with the first one if an intersection was found
            if int_exists:
                split_brep2, int_exists = intersect_solid(
                    int_solids[i + j + 1], int_solids[i])
                int_solids[i + j + 1] = split_brep2

    return int_solids


def intersect_solid(solid, other_solid):
    """Intersect the co-planar faces of one solid Brep using another.

    Args:
        solid: The solid Brep which will be split with intersections.
        other_solid: The other Brep, which will be used to split.

    Returns:
        A tuple with two elements

        -   solid -- The input solid, which has been split.

        -   intersection_exists -- Boolean to note whether an intersection was found
            between the solid and the other_solid. If False, there's no need to
            split the other_solid with the input solid.
    """
    # variables to track the splitting process
    intersection_exists = False  # boolean to note whether an intersection exists
    temp_brep = solid.Split(other_solid, tolerance)
    if len(temp_brep) != 0:
        solid = rg.Brep.JoinBreps(temp_brep, tolerance)[0]
        solid.Faces.ShrinkFaces()
        intersection_exists = True
    return solid, intersection_exists


def overlapping_bounding_boxes(bound_box1, bound_box2):
    """Check if two Rhino bounding boxes overlap within the tolerance.

    This is particularly useful as a check before performing computationally
    intense intersection processes between two bounding boxes. Checking the
    overlap of the bounding boxes is extremely quick given this method's use
    of the Separating Axis Theorem. This method is built into the intersect_solids
    functions in order to improve its calculation time.

    Args:
        bound_box1: The first bound_box to check.
        bound_box2: The second bound_box to check.
    """
    # Bounding box check using the Separating Axis Theorem
    bb1_width = bound_box1.Max.X - bound_box1.Min.X
    bb2_width = bound_box2.Max.X - bound_box2.Min.X
    dist_btwn_x = abs(bound_box1.Center.X - bound_box2.Center.X)
    x_gap_btwn_box = dist_btwn_x - (0.5 * bb1_width) - (0.5 * bb2_width)

    bb1_depth = bound_box1.Max.Y - bound_box1.Min.Y
    bb2_depth = bound_box2.Max.Y - bound_box2.Min.Y
    dist_btwn_y = abs(bound_box1.Center.Y - bound_box2.Center.Y)
    y_gap_btwn_box = dist_btwn_y - (0.5 * bb1_depth) - (0.5 * bb2_depth)

    bb1_height = bound_box1.Max.Z - bound_box1.Min.Z
    bb2_height = bound_box2.Max.Z - bound_box2.Min.Z
    dist_btwn_z = abs(bound_box1.Center.Z - bound_box2.Center.Z)
    z_gap_btwn_box = dist_btwn_z - (0.5 * bb1_height) - (0.5 * bb2_height)

    if x_gap_btwn_box > tolerance or y_gap_btwn_box > tolerance or \
            z_gap_btwn_box > tolerance:
        return False  # no overlap
    return True  # overlap exists


def split_solid_to_floors(building_solid, floor_heights):
    """Extract a series of planar floor surfaces from solid building massing.

    Args:
        building_solid: A closed brep representing a building massing.
        floor_heights: An array of float values for the floor heights, which
            will be used to generate planes that subdivide the building solid.

    Returns:
        floor_breps -- A list of planar, horizontal breps representing the floors
        of the building.
    """
    # get the floor brep at each of the floor heights.
    floor_breps = []
    for hgt in floor_heights:
        story_breps = []
        floor_base_pt = rg.Point3d(0, 0, hgt)
        section_plane = rg.Plane(floor_base_pt, rg.Vector3d.ZAxis)
        floor_crvs = rg.Brep.CreateContourCurves(building_solid, section_plane)
        try:  # Assume a single countour curve has been found
            floor_brep = rg.Brep.CreatePlanarBreps(floor_crvs, tolerance)
        except TypeError:  # An array of contour curves has been found
            floor_brep = rg.Brep.CreatePlanarBreps(floor_crvs)
        if floor_brep is not None:
            story_breps.extend(floor_brep)
        floor_breps.append(story_breps)

    return floor_breps


def geo_min_max_height(geometry):
    """Get the min and max Z values of any input object.

    This is useful as a pre-step before the split_solid_to_floors method.
    """
    bound_box = geometry.GetBoundingBox(rg.Plane.WorldXY)
    return bound_box.Min.Z, bound_box.Max.Z
