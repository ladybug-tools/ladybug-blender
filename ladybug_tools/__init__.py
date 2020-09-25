bl_info = {
    "name": "Ladybug Tools",
    "author": "Dion Moult",
    "version": (0, 0, 999999),
    "blender": (2, 90, 0),
    "location": "Node Editor",
    "category": "Node",
    "description": "Ladybug, Honeybee, Butterfly, and Dragonfly for Blender",
    "warning": "",
    "wiki_url": "https://wiki.osarch.org/",
    "tracker_url": "https://github.com/ladybug-tools/ladybug-blender"
}

import os
import site

cwd = os.path.dirname(os.path.realpath(__file__))
site.addsitedir(os.path.join(cwd, "lib"))

import sys
import importlib
import nodeitems_utils
import sverchok
from sverchok.core import sv_registration_utils, make_node_list
from sverchok.utils import auto_gather_node_classes, get_node_class_reference
from sverchok.menu import SverchNodeItem, SverchNodeCategory, register_node_panels
from sverchok.utils.extra_categories import register_extra_category_provider, unregister_extra_category_provider
from sverchok.ui.nodeview_space_menu import make_extra_category_menus
from sverchok.utils.logging import info, debug

def nodes_index():
    return [("Ladybug", [
        ("ladybug.LB_Out", "SvLBOut"),
        # Generated nodes
        ("ladybug.LB_Solar_MRT_from_Solar_Components", "SvComponentSolarMRT"),
        ("ladybug.LB_Import_Location", "SvImportLoc"),
        ("ladybug.LB_Calculate_HOY", "SvHOY"),
        ("ladybug.LB_Import_EPW", "SvImportEPW"),
        ("ladybug.LB_Unit_Converter", "SvUnits"),
        ("ladybug.LB_Legend_Parameters_Categorized", "SvLegendParCategorized"),
        ("ladybug.LB_Generate_Point_Grid", "SvGenPts"),
        ("ladybug.LB_Apply_Analysis_Period", "SvApplyPer"),
        ("ladybug.LB_UTCI_Comfort", "SvUTCI"),
        ("ladybug.LB_To_IP", "SvToIP"),
        ("ladybug.LB_Construct_Data_Type", "SvConstrType"),
        ("ladybug.LB_Wind_Rose", "SvWindRose"),
        ("ladybug.LB_Construct_Data", "SvPlusData"),
        ("ladybug.LB_Orient_to_Camera", "SvOrientCam"),
        ("ladybug.LB_Arithmetic_Operation", "SvArithOp"),
        ("ladybug.LB_Construct_Location", "SvConstrLoc"),
        ("ladybug.LB_Import_DDY", "SvImportDDY"),
        ("ladybug.LB_Degree_Days", "SvHDD_CDD"),
        ("ladybug.LB_Sky_Dome", "SvSkyDome"),
        ("ladybug.LB_Download_Weather", "SvDownloadEPW"),
        ("ladybug.LB_Deconstruct_Data", "SvXData"),
        ("ladybug.LB_EPW_to_DDY", "SvEPWtoDDY"),
        ("ladybug.LB_Analysis_Period", "SvAnalysisPeriod"),
        ("ladybug.LB_Open_Directory", "SvOpenDir"),
        ("ladybug.LB_Adaptive_Comfort", "SvAdaptive"),
        ("ladybug.LB_Data_to_Legacy", "SvToLegacy"),
        ("ladybug.LB_Direct_Sun_Hours", "SvDirectSunHours"),
        ("ladybug.LB_Humidity_Metrics", "SvHumidityR"),
        ("ladybug.LB_Incident_Radiation", "SvIncidentRadiation"),
        ("ladybug.LB_Open_File", "SvOpenFile"),
        ("ladybug.LB_Create_Legend", "SvCreateLegend"),
        ("ladybug.LB_View_Percent", "SvViewPercent"),
        ("ladybug.LB_Hourly_Plot", "SvHourlyPlot"),
        ("ladybug.LB_Adaptive_Comfort_Parameters", "SvAdaptPar"),
        ("ladybug.LB_View_From_Sun", "SvViewFromSun"),
        ("ladybug.LB_To_Unit", "SvToUnit"),
        ("ladybug.LB_Monthly_Chart", "SvMonthlyChart"),
        ("ladybug.LB_Indoor_Solar_MRT", "SvIndoorSolarMRT"),
        ("ladybug.LB_Import_Design_Day", "SvImportDesignDay"),
        ("ladybug.LB_Spatial_Heatmap", "SvHeatmap"),
        ("ladybug.LB_Cumulative_Sky_Matrix", "SvSkyMatrix"),
        ("ladybug.LB_Deconstruct_Location", "SvDecnstrLoc"),
        ("ladybug.LB_Deconstruct_Matrix", "SvXMatrix"),
        ("ladybug.LB_Import_STAT", "SvImportSTAT"),
        ("ladybug.LB_PMV_Comfort_Parameters", "SvPMVPar"),
        ("ladybug.LB_Deconstruct_Header", "SvXHeader"),
        ("ladybug.LB_Visibility_Percent", "SvVisibilityPercent"),
        ("ladybug.LB_SunPath", "SvSunpath"),
        ("ladybug.LB_Solar_Body_Parameters", "SvSolarBodyPar"),
        ("ladybug.LB_Construct_Header", "SvConstrHeader"),
        ("ladybug.LB_Mass_Arithmetic_Operation", "SvMassArithOp"),
        ("ladybug.LB_Real_Time_Incident_Radiation", "SvRTrad"),
        ("ladybug.LB_Color_Range", "SvColRange"),
        ("ladybug.LB_Convert_to_Timestep", "SvToStep"),
        ("ladybug.LB_Apply_Conditional_Statement", "SvStatement"),
        ("ladybug.LB_Deconstruct_Design_Day", "SvDecnstrDesignDay"),
        ("ladybug.LB_Time_Interval_Operation", "SvTimeOp"),
        ("ladybug.LB_Comfort_Statistics", "SvComfStat"),
        ("ladybug.LB_Relative_Humidity_from_Dew_Point", "SvRelHumid"),
        ("ladybug.LB_HOY_to_DateTime", "SvDateTime"),
        ("ladybug.LB_Outdoor_Solar_MRT", "SvOutdoorSolarMRT"),
        ("ladybug.LB_To_SI", "SvToSI"),
        ("ladybug.LB_Legend_Parameters", "SvLegendPar"),
        ("ladybug.LB_EPWmap", "SvEPWMap"),
        ("ladybug.LB_PMV_Comfort", "SvPMV"),
    ])]

def make_node_list():
    modules = []
    base_name = "ladybug_tools.nodes"
    index = nodes_index()
    for category, items in index:
        for module_name, node_name in items:
            module = importlib.import_module(f".{module_name}", base_name)
            modules.append(module)
    return modules

imported_modules = make_node_list()

reload_event = False

import bpy

def register_nodes():
    node_modules = make_node_list()
    for module in node_modules:
        module.register()
    info("Registered %s nodes", len(node_modules))

def unregister_nodes():
    global imported_modules
    for module in reversed(imported_modules):
        module.unregister()

def make_menu():
    menu = []
    index = nodes_index()
    for category, items in index:
        identifier = "LADYBUG_TOOLS_" + category.replace(' ', '_')
        node_items = []
        for item in items:
            nodetype = item[1]
            rna = get_node_class_reference(nodetype)
            if not rna:
                info("Node `%s' is not available (probably due to missing dependencies).", nodetype)
            else:
                node_item = SverchNodeItem.new(nodetype)
                node_items.append(node_item)
        if node_items:
            cat = SverchNodeCategory(
                        identifier,
                        category,
                        items=node_items
                    )
            menu.append(cat)
    return menu

class SvExCategoryProvider(object):
    def __init__(self, identifier, menu):
        self.identifier = identifier
        self.menu = menu

    def get_categories(self):
        return self.menu

our_menu_classes = []

def register():
    global our_menu_classes

    debug("Registering ladybug_tools")

    register_nodes()
    extra_nodes = importlib.import_module(".nodes", "ladybug_tools")
    auto_gather_node_classes(extra_nodes)
    menu = make_menu()
    menu_category_provider = SvExCategoryProvider("LADYBUG_TOOLS", menu)
    register_extra_category_provider(menu_category_provider) #if 'LADYBUG_TOOLS' in nodeitems_utils._node_categories:
    nodeitems_utils.register_node_categories("LADYBUG_TOOLS", menu)
    our_menu_classes = make_extra_category_menus()

def unregister():
    global our_menu_classes
    if 'LADYBUG_TOOLS' in nodeitems_utils._node_categories:
        nodeitems_utils.unregister_node_categories("LADYBUG_TOOLS")
    for clazz in our_menu_classes:
        try:
            bpy.utils.unregister_class(clazz)
        except Exception as e:
            print("Can't unregister menu class %s" % clazz)
            print(e)
    unregister_extra_category_provider("LADYBUG_TOOLS")
    unregister_nodes()
