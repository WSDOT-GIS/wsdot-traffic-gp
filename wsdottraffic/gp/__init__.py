"""wsdottraffic.gp
Queries the WSDOT Traveler Info REST endpoints and populates a table using the
results.
"""
import os
from os.path import join, dirname
from collections import OrderedDict
import re
import json
import zipfile
import warnings
import logging

import arcpy
from ..parseutils import split_camel_case
from .. import get_traveler_info
from ..resturls import URLS
from .domaintools import add_domain
from ..jsonhelpers import CustomEncoder
from ..dicttools import dict_has_all_keys

_LOGGER = logging.getLogger(__name__)

# JSON files are in the same directory as this script. This function
# returns that directory.
def _get_json_dir():
    return dirname(__file__)

# Load list info for creating geodatabase domains.
with open(join(_get_json_dir(), "./domains.json"), "r") as domains_file:
    DOMAINS = json.load(domains_file, object_pairs_hook=OrderedDict)

# This dictionary defines the fields in each table.  Each field's dictionary
# entry can either contain a single string value indicating the field type, or
# a dictionary with parameters for the arcpy.management.AddField function
# (excluding in_table and field_name, which are already provided by the
# dictionary keys).
with open(join(_get_json_dir(), "./tabledefs.json"), "r") as def_file:
    TABLE_DEFS_DICT_DICT = json.load(def_file, object_pairs_hook=OrderedDict)


def _are_coords_valid(*coords):
    """Returns False if a coordinate is either 0 or None, True otherwise.

    Parameters
    ----------
    coords: one or more number values.
    """
    for coord in coords:
        if coord == 0 or coord is None:
            return False
    return True


def _create_multipoint(*args):
    """Creates an arcpy.Multipoint from a series of numbers with an even number
    of elements.
    """
    if len(args) % 2 != 0:
        raise ValueError("The number of arguments must be even.")
    elif not args:
        return None

    # Loop through the input numbers as XY pairs.
    # Create an array of points.
    i = 0
    arc_array = arcpy.Array()
    while i < len(args):
        x = args[i]
        i += 1
        y = args[i]
        i += 1
        # Only add the coordinates if they are valid.
        if _are_coords_valid(x, y):
            arc_array.add(arcpy.Point(x, y))

    if not arc_array:
        return None

    # Create a Multipoint using the point array.
    shape = arcpy.Multipoint(arc_array)
    return shape


def create_table(table_path, table_def_dict=None,
                 data_list=None,
                 templates_workspace=None):
    """Creates a table for one of the Traveler API REST Endpoints' data.

    Parameters
    ----------
    tablePath : str
        The path where the new table will be created. If this path already
        exists than the existing table will be truncated.
    tableDefDict : dict, optional
        A dict that defines the fields that will be created.  If omitted, the
        fields will be determined by the table path.
    dataList : list, optional
        A list of data returned from wsdottraffic.get_traveler_info that will
        be used to populate the table.
    templatesWorkspace : str, optional
        The path to a geodatabase containing template tables.  This will be
        faster than using the AddField tool.
    """
    POINT_X_FIELD = "Longitude"
    POINT_Y_FIELD = "Latitude"

    MULTIPOINT_X1_FIELD = "StartLongitude"
    MULTIPOINT_Y1_FIELD = "StartLatitude"
    MULTIPOINT_X2_FIELD = "EndLongitude"
    MULTIPOINT_Y2_FIELD = "EndLatitude"

    POINT_FIELD_NAMES = (POINT_X_FIELD, POINT_Y_FIELD)
    MULTIPOINT_FIELD_NAMES = (MULTIPOINT_X1_FIELD, MULTIPOINT_Y1_FIELD,
                              MULTIPOINT_X2_FIELD, MULTIPOINT_Y2_FIELD)

    table_name = os.path.split(table_path)[1]

    if table_def_dict is None:
        table_def_dict = TABLE_DEFS_DICT_DICT[table_name]
    field_dict = table_def_dict["fields"]

    # Check to see if geometry type and fields are explicitly specified.
    if "geometryInfo" in table_def_dict:
        geometry_info = table_def_dict["geometryInfo"]
        is_point = re.match("POINT", geometry_info["geometryType"],
                            re.IGNORECASE) is not None
        if is_point:
            if "fields" in geometry_info:
                POINT_FIELD_NAMES = geometry_info["fields"]
            is_polyline = False
    else:
        is_point = dict_has_all_keys(field_dict, *POINT_FIELD_NAMES)
        is_polyline = dict_has_all_keys(field_dict, *MULTIPOINT_FIELD_NAMES)
    if not (is_point or is_polyline):
        raise ValueError(
            "%s does not contain fields necessary for Shape" %
            field_dict.keys())
    elif is_point and is_polyline:
        # If input contains fields for both shape types,
        # pick one, since feature class can't have both.
        is_point = False

    # Create the table if it does not already exist.
    if not arcpy.Exists(table_path):
        # Check to see if the fieldDict parameter was provided.
        # If not, get the fields from the fieldsDict based on
        # the table name in tablePath.
        workspace, fc_name = os.path.split(table_path)
        if (templates_workspace is not None and
                arcpy.Exists(
                    os.path.join(templates_workspace, table_name))):
            template_path = os.path.join(templates_workspace, table_name)
            _LOGGER.info(
                "Creating table %(table_path)s using template " +
                "%s(template_path)...",
                {"table_path": table_path, "template_path": template_path})
            if is_point:
                arcpy.management.CreateFeatureclass(
                    workspace, fc_name, "POINT", template_path,
                    "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", template_path)
            elif is_polyline:
                arcpy.management.CreateFeatureclass(
                    workspace, fc_name, "MULTIPOINT", template_path,
                    "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", template_path)
            else:
                arcpy.management.CreateTable(
                    workspace, fc_name, template=template_path)
        else:
            _LOGGER.info("Creating table %(table_path)s...",
                         {"table_path", table_path})
            # _LOGGER.warning(
            #     "Creating table without a template.  Table creation would " +
            #     "be faster if using a template.")
            ignored_fields = ()
            if is_point:
                ignored_fields = POINT_FIELD_NAMES
                arcpy.management.CreateFeatureclass(
                    workspace, fc_name, "POINT",
                    spatial_reference=arcpy.SpatialReference(4326))
            elif is_polyline:
                ignored_fields = MULTIPOINT_FIELD_NAMES
                arcpy.management.CreateFeatureclass(
                    workspace, fc_name, "MULTIPOINT",
                    spatial_reference=arcpy.SpatialReference(4326))
            else:
                arcpy.management.CreateTable(workspace, fc_name)

            _LOGGER.info("Adding fields...")

            _add_fields(field_dict, table_path, ignored_fields)
            _add_domains(table_def_dict, table_path)

    else:
        _LOGGER.info("Truncating table %(table_path)s...",
                     {"table_path": table_path})
        # Truncate the table if it already exists
        arcpy.management.DeleteRows(table_path)

    if data_list is not None:
        bad_value_re = re.compile(r"^(?P<error>.+) \[(?P<field>\w+)\]$",
                                  re.MULTILINE)
        _LOGGER.info("Adding data to %s...", table_path)
        fields = list(field_dict.keys())

        if is_polyline:
            for field in MULTIPOINT_FIELD_NAMES:
                fields.remove(field)
            fields.append("SHAPE@")
        elif is_point:
            for field in POINT_FIELD_NAMES:
                fields.remove(field)
            fields.append("SHAPE@XY")
        rowcounter = 0
        failcounter = 0
        with arcpy.da.InsertCursor(table_path, fields) as cursor:
            for item in data_list:
                row = []
                for key in fields:
                    if (key == "SHAPE@XY" and
                            dict_has_all_keys(item, *POINT_FIELD_NAMES)):
                        x, y = map(item.get, POINT_FIELD_NAMES, (None,) * 2)
                        if not _are_coords_valid(x, y):
                            _LOGGER.warning(
                                "Invalid point coordinates. Setting to NULL." +
                                "\n%s\n%s",
                                table_path,
                                json.dumps(item, cls=CustomEncoder))
                            row.append(None)
                        else:
                            row.append((x, y))
                    elif (key == "SHAPE@" and
                          dict_has_all_keys(item, *MULTIPOINT_FIELD_NAMES)):
                        x1, y1, x2, y2 = map(
                            item.get, MULTIPOINT_FIELD_NAMES, (None,) * 4)
                        shape = _create_multipoint(x1, y1, x2, y2)

                        if not shape:
                            # If the multipoint fields didn't have valid
                            # values, check for point field definitions.
                            if dict_has_all_keys(*POINT_FIELD_NAMES):
                                x, y = map(
                                    item.get, POINT_FIELD_NAMES, (None,) * 2)
                                shape = _create_multipoint(x, y)
                            else:
                                _LOGGER.warning("No valid multipoint\n%s\n%s",
                                                table_path, item)
                        row.append(shape)
                    elif key not in item:
                        row.append(None)
                    else:
                        val = item[key]
                        row.append(val)
                try:
                    cursor.insertRow(row)
                except RuntimeError as err_inst:
                    # Sample args value of errInst:
                    # tuple: ('ERROR 999999: Error executing function.\nThe row
                    # contains a bad value. [CVRestrictions]\nThe row contains
                    # a bad value. [RestrictionComment]',)

                    ex_message = ("Error inserting %(row)s into %(table)s, " +
                                  "which has these fields: %(fields)s")
                    warnings.warn(ex_message % {
                        "row": row,
                        "table": table_name,
                        "fields": fields
                    })

                    if err_inst.args:
                        msg_template = ("Bad value in [%s] field.\n" +
                                        "Length is %s.\n" +
                                        "Value is %s\n" + "%s")
                        for arg in err_inst.args:
                            matches = bad_value_re.findall(arg)
                            # [(u'The row contains a bad value.',
                            # u'CVRestrictions'), (u'The row contains a bad
                            # value.', u'RestrictionComment')]
                            for match in matches:
                                error_msg, field_name = match
                                if field_name != table_name:
                                    warnings.warn(msg_template % (
                                        field_name, len(item[field_name]),
                                        item[field_name], error_msg))
                                else:
                                    pass
                    else:
                        warnings.warn(
                            "Error adding row to %(table).\n" +
                            "%(err_inst)s\n%(item)s", {
                                "table": table_name,
                                "err_inst": err_inst,
                                "item": item})
                    failcounter += 1
                    raise
                else:
                    rowcounter += 1
        _LOGGER.info(
            "Added %(rowcounter)d rows to %(table_path)s." +
            " Failed to add %(failcounter)d rows.", {
                "rowcounter": rowcounter, "table_path": table_path,
                "failcounter": failcounter})


def _add_fields(field_dict, table_path, ignored_fields=None):
    """Adds fields to a table

    Parameters
    ----------

    field_dict
        dict - a dict of dicts that describe fields to be added to the table.
    table_path
        str - The path of the table or feature class that the fields will be
        added to.
    ignored_fields (optional)
        A set of field name strings that will NOT be added to the table.
    """
    # Add the columns
    for key in field_dict:
        if ignored_fields is not None and key in ignored_fields:
            continue
        val = field_dict[key]
        if isinstance(val, dict):
            if "field_name" not in val:
                val["field_name"] = key
            if "field_alias" not in val:
                val["field_alias"] = split_camel_case(
                    val["field_name"])
            arcpy.management.AddField(table_path, **val)
        else:
            arcpy.management.AddField(table_path, key, val,
                                      field_alias=split_camel_case(key))


def _add_domains(table_def_dict, table_path):
    """Adds domains to table if they haven't already been specified.
    """
    # Exit without doing anything if the current table has no associated
    # domains.
    if "domains" not in table_def_dict:
        return
    # Key is field name, value is domain name
    domain_dict = table_def_dict["domains"]
    workspace = os.path.split(table_path)[0]

    for field_name, domain_name in domain_dict.items():
        domain_info = DOMAINS[domain_name]
        add_domain(
            workspace,
            domain_name,
            domain_info.get("domain_description"),
            domain_info.get("field_type", "SHORT"),
            domain_info.get("domain_type", "CODED"),
            domain_info.get("values"),
            False)
        arcpy.management.AssignDomainToField(table_path, field_name,
                                             domain_name)
