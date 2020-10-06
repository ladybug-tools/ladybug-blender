import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import multi_socket, updateNode, zip_long_repeat

from ladybug_tools.text import LadybugText
from ladybug_tools.colorize import ColoredPoint
from ladybug_geometry.geometry2d.line import LineSegment2D
from ladybug_geometry.geometry2d.arc import Arc2D
from ladybug_geometry.geometry3d.arc import Arc3D
from ladybug_geometry.geometry2d.mesh import Mesh2D
from ladybug_geometry.geometry3d.mesh import Mesh3D
from ladybug_geometry.geometry2d.pointvector import Point2D
from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry2d.polyline import Polyline2D
from ladybug_geometry.geometry3d.polyline import Polyline3D

from math import pi, sin, cos
from mathutils import Vector, Matrix

class SvLBOutOp(bpy.types.Operator):
    bl_idname = "node.sv_lb_out"
    bl_label = "LB Out"
    bl_options = {'UNDO'}

    idtree: StringProperty(default='')
    idname: StringProperty(default='')
    has_baked: bpy.props.BoolProperty(name='Has Baked', default=False)

    def execute(self, context):
        node = bpy.data.node_groups[self.idtree].nodes[self.idname]
        node.refresh()
        return {'FINISHED'}


class SvLBOut(bpy.types.Node, SverchCustomTreeNode):
    bl_idname = 'SvLBOut'
    bl_label = 'LB Out'
    sv_icon = 'LB_OUT'
    base_name = 'geometry '
    multi_socket_type = 'SvStringsSocket'
    has_baked: bpy.props.BoolProperty(name='Has Baked', default=False)

    def sv_init(self, context):
        self.inputs.new('SvStringsSocket', 'geometry')
        self.outputs.new('SvVerticesSocket', "verts")
        self.outputs.new('SvStringsSocket', "edges")
        self.outputs.new('SvStringsSocket', "faces")

    def sv_update(self):
        if len(self.outputs) > 0:
            multi_socket(self, min=1)

    def draw_buttons(self, context, layout):
        self.wrapper_tracked_ui_draw_op(layout, 'node.sv_lb_out', icon='FILE_REFRESH', text='Refresh')

    def refresh(self):
        self.has_baked = False
        self.process()

    def process(self):
        if self.has_baked:
            return

        self.v = []
        self.e = []
        self.f = []
        self.text_v = []
        self.text_s = []
        self.blender_v = []
        self.blender_colored_v = []

        for socket in self.inputs:
            if not (socket.is_linked and socket.links):
                continue
            for geometries in socket.sv_get():
                for geometry in geometries:
                    self._process_geometry(geometry)

        self.create_blender_colored_v()
        self.create_wireframe([Vector(xyz) for xyz in self.blender_v], [])
        self.outputs['verts'].sv_set(self.v)
        self.outputs['edges'].sv_set(self.e)
        self.outputs['faces'].sv_set(self.f)
        self.has_baked = True

    def _process_geometry(self, geometry):
        if isinstance(geometry, (tuple, list)):
            for g in geometry:
                self._process_geometry(g)
            return
        self._process_sverchok_geometry(geometry)
        self._process_blender_geometry(geometry)

    def _process_sverchok_geometry(self, geometry):
        if isinstance(geometry, Arc2D):
            self.sverchok_from_arc2d(geometry)
        elif isinstance(geometry, Arc3D):
            self.sverchok_from_arc3d(geometry)
        elif isinstance(geometry, LineSegment2D):
            self.sverchok_from_linesegment2d(geometry)
        elif isinstance(geometry, (Point2D, Point3D)):
            self.sverchok_from_point(geometry)
        elif isinstance(geometry, (Polyline2D, Polyline3D)):
            self.sverchok_from_polyline(geometry)
        elif isinstance(geometry, (float, int, tuple, list, str)):
            pass # The user probably connected a non geometry node
        else:
            print('WARNING: geometry {} not yet supported in Sverchok: {}'.format(type(geometry), geometry))

    def _process_blender_geometry(self, geometry):
        if isinstance(geometry, Arc2D):
            self.blender_from_arc2d(geometry)
        elif isinstance(geometry, Arc3D):
            self.blender_from_arc3d(geometry)
        elif isinstance(geometry, ColoredPoint):
            self.blender_colored_v.append(geometry)
        elif isinstance(geometry, LineSegment2D):
            self.blender_from_linesegment2d(geometry)
        elif isinstance(geometry, LadybugText):
            self.blender_from_text(geometry)
        elif isinstance(geometry, (Mesh2D, Mesh3D)):
            self.blender_from_mesh(geometry)
        elif isinstance(geometry, (Point2D, Point3D)):
            # Points are much more efficient in a single mesh
            self.blender_v.append(self.from_point(geometry))
        elif isinstance(geometry, (Polyline2D, Polyline3D)):
            self.blender_from_polyline(geometry)
        elif isinstance(geometry, (float, int, tuple, list, str)):
            pass # The user probably connected a non geometry node
        else:
            print('WARNING: geometry {} not yet supported in Blender: {}'.format(type(geometry), geometry))

    def from_linesegment2d(self, line, z=0):
        """Rhino LineCurve from ladybug LineSegment2D."""
        v = [(line.p1.x, line.p1.y, z), (line.p2.x, line.p2.y, z)]
        return v, [[0, 1]]

    def sverchok_from_linesegment2d(self, line, z=0):
        v, e = self.from_linesegment2d(line, z)
        self.v.append(v)
        self.e.append(e)
        self.f.append([[0]]) # Hack

    def blender_from_linesegment2d(self, line, z=0):
        self.create_wireframe(*self.from_linesegment2d(line))

    def from_arc2d(self, arc, z=0):
        """Rhino Arc from ladybug Arc2D."""
        arc_perimeter = (arc.a2-arc.a1)*arc.r
        # TODO: unhardcode facetation of 32 times
        v = []
        e = []
        step = (arc.a2 - arc.a1) / 32
        for i in range(0, 32 + 1):
            a = arc.a1 + i * step
            v.append((cos(a)*arc.r+arc.c.x, sin(a)*arc.r+arc.c.y, z))
            e.append((i, i+1))
        del e[-1]
        return v, e

    def sverchok_from_arc2d(self, arc, z=0):
        v, e = self.from_arc2d(arc, z)
        self.v.append(v)
        self.e.append(e)
        self.f.append([[0]]) # Hack

    def blender_from_arc2d(self, arc, z=0):
        self.create_wireframe(*self.from_arc2d(arc))

    def from_arc3d(self, arc):
        """Rhino Arc from ladybug Arc3D."""
        if arc.is_circle:
            assert False, 'I have not yet built circular arcs'
        else:
            # TODO: unhardcode facetation of 32 times
            v = []
            e = []
            a1 = arc.a1
            # I'm assuming that a1 and a2 is _always_ ordered from small to large
            a2 = arc.a2 if arc.a1 < arc.a2 else arc.a2 + (2 * pi)
            step = (a2 - a1) / 32
            p = arc.plane
            mat = Matrix((
                    (p.x.x, p.y.x, p.n.x, p.o.x),
                    (p.x.y, p.y.y, p.n.y, p.o.y),
                    (p.x.z, p.y.z, p.n.z, p.o.z),
                    (0, 0, 0, 1),
                ))
            for i in range(0, 32 + 1):
                a = a1 + i * step
                co = Vector((cos(a)*arc.radius, sin(a)*arc.radius, 0))
                v.append(mat @ co)
                e.append((i, i+1))
            del e[-1]
        return v, e

    def sverchok_from_arc3d(self, arc):
        v, e = self.from_arc3d(arc)
        self.v.append(v)
        self.e.append(e)
        self.f.append([[0]]) # Hack

    def blender_from_arc3d(self, arc):
        self.create_wireframe(*self.from_arc3d(arc))

    def blender_from_mesh(self, mesh, z=0):
        """Rhino Mesh from ladybug Mesh2D."""
        data = bpy.data.meshes.new('Ladybug Mesh')
        data.from_pydata([Vector((v.x, v.y, v.z if hasattr(v, 'z') else 0)) for v in mesh.vertices], [], mesh.faces)
        def get_material_name(color):
            return 'ladybug-{}-{}-{}-{}'.format(color.r, color.g, color.b, color.a)

        if mesh.is_color_by_face:
            colors = list(set(mesh.colors))
            material_to_slot = {}
            for i, color in enumerate(colors):
                name = get_material_name(color)
                material_to_slot[name] = i
                material = bpy.data.materials.get(name)
                if not material:
                    material = bpy.data.materials.new(name)
                    material.diffuse_color = (color.r / 255, color.g / 255, color.b / 255, color.a / 255)
                    material.specular_intensity = 0
                data.materials.append(material)
            material_index = [material_to_slot[get_material_name(c)] for c in mesh.colors]
            data.polygons.foreach_set('material_index', material_index)
        else:
            material = bpy.data.materials.get('LB_VCol')
            if not material:
                material = bpy.data.materials.new('LB_VCol')
                material.use_nodes = True
                for node in material.node_tree.nodes:
                    if node.type == 'OUTPUT_MATERIAL':
                        output_node = node
                        break
                emission = material.node_tree.nodes.new(type='ShaderNodeEmission')
                attribute = material.node_tree.nodes.new(type='ShaderNodeAttribute')
                attribute.attribute_name = 'LB_Col'
                material.node_tree.links.new(attribute.outputs[0], emission.inputs[0])
                material.node_tree.links.new(emission.outputs[0], output_node.inputs[0])
            data.materials.append(material)
            data.vertex_colors.new(name='LB_Col')
            for polygon in data.polygons:
                for i, vi in enumerate(polygon.vertices):
                    loop_index = polygon.loop_indices[i]
                    color = mesh.colors[vi]
                    data.vertex_colors['LB_Col'].data[loop_index].color = (color.r / 255, color.g / 255, color.b / 255, color.a / 255)
        obj = bpy.data.objects.new('Ladybug Mesh', data)
        bpy.context.scene.collection.objects.link(obj)

    def from_point(self, point):
        """Rhino Point3d from ladybug Point3D."""
        return (point.x, point.y, point.z if hasattr(point, 'z') else 0)

    def sverchok_from_point(self, point):
        self.v.append([self.from_point(point)])
        self.e.append([[0, 0]]) # Hack
        self.f.append([[0]]) # Hack

    def from_polyline(self, polyline, z=0):
        """Rhino closed PolyLineCurve from ladybug Polyline3D."""
        v = [(p.x, p.y, p.z if hasattr(p, 'z') else z) for p in polyline.vertices]
        e = [(i, i+1) for i in range(0, len(polyline.vertices)-1)]
        if polyline.interpolated:
            print('TODO: interpolate this polyline')
            return v, e
            self.v.append(v)
            self.e.append(e)
            self.f.append([[0]]) # Hack
        else:
            return v, e
            self.v.append(v)
            self.e.append(e)
            self.f.append([[0]]) # Hack

    def sverchok_from_polyline(self, polyline, z=0):
        v, e = self.from_polyline(polyline, z)
        self.v.append(v)
        self.e.append(e)
        self.f.append([[0]]) # Hack

    def blender_from_polyline(self, polyline, z=0):
        self.create_wireframe(*self.from_polyline(polyline, z))

    def blender_from_text(self, text):
        data = bpy.data.curves.new('Ladybug Text', 'FONT')
        data.body = text.text
        data.size = text.height * 2

        if text.horizontal_alignment == 0:
            data.align_x = 'LEFT'
        elif text.horizontal_alignment == 1:
            data.align_x = 'CENTER'
        elif text.horizontal_alignment == 2:
            data.align_x = 'RIGHT'

        if text.vertical_alignment <= 2:
            data.align_y = 'TOP'
        elif text.vertical_alignment <= 4:
            data.align_y = 'CENTER'
        elif text.vertical_alignment <= 6:
            data.align_y = 'BOTTOM'

        name = 'ladybug-0-0-0-255'
        material = bpy.data.materials.get(name)
        if not material:
            material = bpy.data.materials.new(name)
            material.diffuse_color = (0, 0, 0, 255)
            material.specular_intensity = 0
        data.materials.append(material)

        obj = bpy.data.objects.new('Ladybug Text', data)
        obj.location = (text.plane.o.x, text.plane.o.y, text.plane.o.z)
        bpy.context.scene.collection.objects.link(obj)

    def create_blender_colored_v(self):
        if not self.blender_colored_v:
            return
        import numpy as np
        from space_view3d_point_cloud_visualizer import PCVControl
        obj = bpy.data.objects.new('Ladybug Colored Points', None)
        vs = [(cv.point.x, cv.point.y, cv.point.z if hasattr(cv.point, 'z') else 0) for cv in self.blender_colored_v]
        cs = [(cv.color.r/255, cv.color.g/255, cv.color.b/255) for cv in self.blender_colored_v]
        PCVControl(obj).draw(vs, [], cs)
        bpy.context.scene.collection.objects.link(obj)

    def create_wireframe(self, v, e):
        data = bpy.data.meshes.new('Ladybug Wireframe')
        data.from_pydata([Vector(xyz) for xyz in v], e, [])
        obj = bpy.data.objects.new('Ladybug Wireframe', data)
        bpy.context.scene.collection.objects.link(obj)


def register():
    bpy.utils.register_class(SvLBOutOp)
    bpy.utils.register_class(SvLBOut)

def unregister():
    bpy.utils.unregister_class(SvLBOutOp)
    bpy.utils.unregister_class(SvLBOut)
