import bpy
import sverchok.core.socket_conversions
from bpy.types import NodeSocket
from bpy.props import StringProperty
from sverchok.core.sockets import SvSocketCommon, process_from_socket


# Monkey-patch!
def _monkey_get_lenient_socket_types():
    return ['SvLBSocket', 'SvStringsSocket', 'SvObjectSocket', 'SvColorSocket', 'SvVerticesSocket']


class SvLBSocketName(bpy.types.Operator):
    bl_idname = "node.sv_lb_socket_name"
    bl_label = "LB Socket Name"
    bl_options = {'UNDO'}

    idtree: StringProperty(default='')
    idname: StringProperty(default='')

    tooltip: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        return properties.tooltip

    def execute(self, context):
        return {'FINISHED'}


class SvLBSocket(NodeSocket, SvSocketCommon):
    bl_idname = "SvLBSocket"
    bl_label = "Strings Socket"

    color = (0.6, 1.0, 0.6, 1.0)

    quick_link_to_node: StringProperty()  # this can be overridden by socket instances

    default_property_type: bpy.props.EnumProperty(items=[(i, i, '') for i in ['float', 'int']])
    default_float_property: bpy.props.FloatProperty(update=process_from_socket)
    default_int_property: bpy.props.IntProperty(update=process_from_socket)

    tooltip: bpy.props.StringProperty()

    @property
    def default_property(self):
        return self.default_float_property if self.default_property_type == 'float' else self.default_int_property

    def draw(self, context, layout, node, text):
        if not self.tooltip:
            self.tooltip = ''

        # just handle custom draw..be it input or output.
        if self.custom_draw:
            # does the node have the draw function referred to by
            # the string stored in socket's custom_draw attribute
            if hasattr(node, self.custom_draw):
                getattr(node, self.custom_draw)(self, context, layout)

        elif self.is_linked:  # linked INPUT or OUTPUT
            layout.operator('node.sv_lb_socket_name',
                    text=self.get_prop_name()[3:] or self.label or text, emboss=False).tooltip = self.tooltip


        elif self.is_output:  # unlinked OUTPUT
            #layout.label(text=self.label or text)
            layout.operator('node.sv_lb_socket_name',
                    text=self.label or text, emboss=False).tooltip = self.tooltip

        else:  # unlinked INPUT
            if self.get_prop_name():  # has property
                self.draw_property(layout, prop_origin=node, prop_name=self.get_prop_name())

            elif self.use_prop:  # no property but use default prop
                self.draw_property(layout)

            else:  # no property and not use default prop
                self.draw_quick_link(context, layout, node)
                layout.label(text=self.label or text)

    def draw_property(self, layout, prop_origin=None, prop_name=None):
        if prop_origin and prop_name:
            row = layout.row(align=True)
            if not self.tooltip:
                self.tooltip = ''
            op = row.operator('node.sv_lb_socket_name', text=prop_name[3:], emboss=False).tooltip = self.tooltip
            row.prop(prop_origin, prop_name, text='')
        elif self.use_prop:
            if self.default_property_type == 'float':
                layout.prop(self, 'default_float_property', text=self.name)
            elif self.default_property_type == 'int':
                layout.prop(self, 'default_int_property', text=self.name)

def register():
    bpy.utils.register_class(SvLBSocketName)
    bpy.utils.register_class(SvLBSocket)
    sverchok.core.socket_conversions.DefaultImplicitConversionPolicy.get_lenient_socket_types = _monkey_get_lenient_socket_types

def unregister():
    bpy.utils.unregister_class(SvLBSocket)
    bpy.utils.unregister_class(SvLBSocketName)
