import bpy
from bpy.types import NodeSocket
from bpy.props import StringProperty
from sverchok.core.sockets import SvSocketCommon, process_from_socket

class SvLBSocket(NodeSocket, SvSocketCommon):
    bl_idname = "SvLBSocket"
    bl_label = "Strings Socket"

    color = (0.6, 1.0, 0.6, 1.0)

    quick_link_to_node: StringProperty()  # this can be overridden by socket instances

    default_property_type: bpy.props.EnumProperty(items=[(i, i, '') for i in ['float', 'int']])
    default_float_property: bpy.props.FloatProperty(update=process_from_socket)
    default_int_property: bpy.props.IntProperty(update=process_from_socket)

    @property
    def default_property(self):
        return self.default_float_property if self.default_property_type == 'float' else self.default_int_property

    def draw_property(self, layout, prop_origin=None, prop_name=None):
        if prop_origin and prop_name:
            row = layout.row(align=True)
            row.label(text=prop_name[3:])
            row.prop(prop_origin, prop_name, text='')
        elif self.use_prop:
            if self.default_property_type == 'float':
                layout.prop(self, 'default_float_property', text=self.name)
            elif self.default_property_type == 'int':
                layout.prop(self, 'default_int_property', text=self.name)

def register():
    print('registering')
    bpy.utils.register_class(SvLBSocket)

def unregister():
    bpy.utils.unregister_class(SvLBSocket)
