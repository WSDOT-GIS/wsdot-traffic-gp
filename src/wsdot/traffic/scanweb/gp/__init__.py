"""ArcGIS Geoprocessing module for Scanweb data
"""

from __future__ import print_function, unicode_literals, absolute_import, division
import os.path
import re
import arcpy
from .. import get_scanweb
from ... import _DEFAULT_ACCESS_CODE
from ...gp import TABLE_DEFS_DICT_DICT

WEATHER_READINGS_TABLE_NAME = "ScanwebWeatherReadings"
SURFACE_TABLE_NAME = "ScanwebSurfaceMeasurements"
SUBSURFACE_TABLE_NAME = "ScanwebSubSurfaceMeasurements"


def create_tables(workspace, force_overwrite=False, template_gdb=None):
    """Creates the tables
    """
    if not arcpy.Exists(workspace):
        # TODO: Use AddIDMessage
        arcpy.AddError("Workspace not found: %s" % workspace)

    tables_created = 0

    if template_gdb and not arcpy.Exists(template_gdb):
        arcpy.AddWarning("Template geodatabase not found: %s" % template_gdb)
        template_gdb = None

    for name in (WEATHER_READINGS_TABLE_NAME, SURFACE_TABLE_NAME, SUBSURFACE_TABLE_NAME):
        table_path = os.path.join(workspace, name)
        template = None
        if template_gdb:
            template = os.path.join(template_gdb, name)
            if not arcpy.Exists(template):
                arcpy.AddWarning("Template Feature Class or table does not exist: %s" % template)
                template = None

        # Skip table creation if table already exists.
        if arcpy.Exists(table_path):
            if force_overwrite:
                arcpy.management.Delete(table_path)
            else:
                continue


        if name == WEATHER_READINGS_TABLE_NAME:
            sr = arcpy.SpatialReference(4326)
            arcpy.management.CreateFeatureclass(
                workspace, name, "POINT", template, "No", "Yes", sr)
        else:
            arcpy.management.CreateTable(workspace, name, template)
        arcpy.AddMessage(arcpy.GetMessages(1))

        fields_dict = TABLE_DEFS_DICT_DICT[name]["fields"]

        if not template:
            # AddFields is setting default value for strings to # instead of Null.
            # Using individual calls to AddField instead to work around this issue.

            # if arcpy.management.AddFields:
            #     field_description = []
            #     for field_name, field_type in fields_dict.items():
            #         field_description.append(
            #             [field_name, field_type, field_name, None, None])
            #     arcpy.management.AddFields(table_path, field_description)
            #     arcpy.AddMessage(arcpy.GetMessages())

            # else:
            #     for field_name, field_type in fields_dict.items():
            #         arcpy.management.AddField(table_path, field_name, field_type)
            #         arcpy.AddMessage(arcpy.GetMessages())
            for field_name, field_type in fields_dict.items():
                arcpy.management.AddField(table_path, field_name, field_type)
                arcpy.AddMessage(arcpy.GetMessages(1))
        tables_created += 1

    if not tables_created:
        return

    if re.match(r"((AlreadyInitialized)|(Available))", arcpy.CheckProduct("arceditor"), re.IGNORECASE):
        try:
            # Create relationships: arcpy.management.AddRelate()
            for table_name in (SURFACE_TABLE_NAME, SUBSURFACE_TABLE_NAME):
                arcpy.management.CreateRelationshipClass(
                    origin_table=os.path.join(
                        workspace, WEATHER_READINGS_TABLE_NAME),
                    destination_table=os.path.join(workspace, table_name),
                    relationship_type="COMPOSITE",
                    forward_label="%sTo%s" % (
                        WEATHER_READINGS_TABLE_NAME, table_name),
                    backward_label="%sFrom%s" % (
                        table_name, WEATHER_READINGS_TABLE_NAME),
                    message_direction="FORWARD",
                    cardinality="ONE_TO_MANY",
                    attributed="NONE",
                    origin_primary_key="StationName",
                    origin_foreign_key="StationName"
                )
        except arcpy.ExecuteError as err:
            print("Could not create relationship classes\n%s" % err)
    else:
        arcpy.AddWarning(
            "Could not create relationship classes because required license was not available")


def populate_feature_classes(workspace, accesscode=_DEFAULT_ACCESS_CODE):
    """Creates or updates ScanWeb feature classes and tables
    """
    create_tables(workspace)
    scanweb_data = get_scanweb(accesscode)

    # Delete the data from the existing tables.
    arcpy.AddMessage("Deleting existing data from tables...")
    for table in (SURFACE_TABLE_NAME, SUBSURFACE_TABLE_NAME, WEATHER_READINGS_TABLE_NAME):
        arcpy.management.DeleteRows("%s/%s" % (workspace, table))
        delete_msgs = arcpy.GetMessages(2)
        if delete_msgs:
            arcpy.AddMessage(delete_msgs)

    fc_fields = list(TABLE_DEFS_DICT_DICT[WEATHER_READINGS_TABLE_NAME]["fields"].keys(
    )) + ["SHAPE@XY", "SHAPE@Z"]
    surface_fields = list(
        TABLE_DEFS_DICT_DICT[SURFACE_TABLE_NAME]["fields"].keys())
    subsurface_fields = list(
        TABLE_DEFS_DICT_DICT[SUBSURFACE_TABLE_NAME]["fields"].keys())
    surface_data = []
    subsurface_data = []

    fc_cursor = arcpy.da.InsertCursor(os.path.join(
        workspace, WEATHER_READINGS_TABLE_NAME), fc_fields)
    with fc_cursor:
        for item in scanweb_data:
            point = None
            if item.Longitude != 0 and item.Latitude != 0:
                point = (item.Longitude, item.Latitude)
            row = list(
                map(item.__dict__.get, fc_fields[:-2])) + [point, item.Elevation]
            try:
                fc_cursor.insertRow(row)
            except RuntimeError as ex:
                arcpy.AddWarning("Error inserting row into %s: %s\n%s" % (WEATHER_READINGS_TABLE_NAME, row, ex))

            station_name = row[1]
            if item.SurfaceMeasurements:
                for m in item.SurfaceMeasurements:
                    mrow = list(map(m.__dict__.get, surface_fields))
                    mrow[0] = station_name
                    surface_data.append(mrow)
            if item.SubSurfaceMeasurements:
                for m in item.SurfaceMeasurements:
                    mrow = list(map(m.__dict__.get, subsurface_fields))
                    mrow[0] = station_name
                    subsurface_data.append(mrow)

    surf_cursor = arcpy.da.InsertCursor(os.path.join(
        workspace, SURFACE_TABLE_NAME), surface_fields)
    with surf_cursor:
        for item in surface_data:
            try:
                surf_cursor.insertRow(item)
            except TypeError:
                print(item)
                raise

    sub_cursor = arcpy.da.InsertCursor(os.path.join(
        workspace, SUBSURFACE_TABLE_NAME), subsurface_fields)
    with sub_cursor:
        for item in subsurface_data:
            sub_cursor.insertRow(item)
