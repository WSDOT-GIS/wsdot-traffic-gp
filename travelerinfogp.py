"""travelerinfogp
Queries the WSDOT Traveler Info REST endpoints and populates a table using the
results.

Parameters:
0   Workspace.  Optional.  Defaults to ./TravelerInfo.gdb.
1   Access Code. Optional if provided via environment variable.
2   Templates GDB. Optional Defaults to "./Data/Templates.gdb"
3   Templates GDB (output)
"""
import os
import re
import json

import arcpy
import parseutils
import travelerinfo
from resturls import URLS
from domaintools import add_domain
from jsonhelpers import CustomEncoder

DOMAINS = {
    "FlowReadingValues": {
        "domain_description": "Possible values for traffic flow sensor points",
        # 0-5, respectively: Unknown, WideOpen, Moderate, Heavy, StopAndGo,
        # NoData
        "values": ["Unknown",
                   "Wide Open",
                   "Moderate",
                   "Heavy",
                   "Stop and Go",
                   "No Data"]
    },
    # 0,1 = BridgeRestriction, RoadRestriction
    "CommercialVehicleRestrictionType": {
        "values": ["Bridge Restriction", "Road Restriction"]
    },
    "Boolean": {
        "values": ["false", "true"]
    }
}

# This dictionary defines the fields in each table.  Each field's dictionary
# entry can either contain a single string value indicating the field type, or
# a dictionary with parameters for the arcpy.management.AddField function
# (excluding in_table and field_name, which are already provided by the
# dictionary keys).
TABLE_DEFS_DICT_DICT = {
    "BorderCrossings": {
        "geometryType": "POINT",
        "fields": {
            "Description": "TEXT",
            "Direction": "TEXT",
            "Latitude": "DOUBLE",
            "Longitude": "DOUBLE",
            "MilePost": "SINGLE",
            "RoadName": "TEXT",
            "CrossingName": "TEXT",
            "Time": "DATE",
            "WaitTime": "SHORT"
        }
    },
    "BridgeClearances": {
        "fields": {
            "LocationID": "GUID",
            "StructureID": "TEXT",
            "StateRouteID": {
                "field_type": "TEXT",
                "field_length": "3"
            },
            "IsConnector": "SHORT",
            "BeginLatitude": "DOUBLE",
            "BeginLongitude": "DOUBLE",
            "BeginMilePost": "SINGLE",
            "EndLatitude": "DOUBLE",
            "EndLongitude": "DOUBLE",
            "EndMilePost": "SINGLE",
            "MaximumVerticalClearance": "TEXT",
            "MaximumVerticalClearanceInches": "LONG",
            "MinimumVerticalClearance": "TEXT",
            "MinimumVerticalClearanceInches": "LONG",
            "LRSRoute": {
                "field_type": "TEXT",
                "field_length": "11"
            },
            "BridgeName": "TEXT"
        },
        "domains": {
            "IsConnector": "Boolean"
        }
    },
    "CVRestrictions": {
        "fields": {
            "BLMaxAxle": "LONG",
            "BridgeName": "TEXT",
            "BridgeNumber": "TEXT",
            "CL8MaxAxle": "LONG",
            "DateEffective": "DATE",
            "DateExpires": "DATE",
            "DatePosted": "DATE",

            "StartRoadwayLocationDescription": "TEXT",
            "StartRoadwayLocationDirection": "TEXT",
            "StartRoadwayLocationLatitude": "DOUBLE",
            "StartRoadwayLocationLongitude": "DOUBLE",
            "StartRoadwayLocationMilePost": "SINGLE",
            "StartRoadwayLocationRoadName": "TEXT",

            "EndRoadwayLocationDescription": "TEXT",
            "EndRoadwayLocationDirection": "TEXT",
            "EndRoadwayLocationLatitude": "DOUBLE",
            "EndRoadwayLocationLongitude": "DOUBLE",
            "EndRoadwayLocationMilePost": "SINGLE",
            "EndRoadwayLocationRoadName": "TEXT",

            "IsDetourAvailable": "SHORT",
            "IsExceptionsAllowed": "SHORT",
            "IsPermanentRestriction": "SHORT",
            "IsWarning": "SHORT",

            "Latitude": "DOUBLE",
            "Longitude": "DOUBLE",
            "LocationDescription": "TEXT",
            "LocationName": "TEXT",
            "MaximumGrossVehicleWeightInPounds": "LONG",
            "RestrictionComment": {
                "field_type": "TEXT",
                "field_length": 800
            },
            "RestrictionHeightInInches": "LONG",
            "RestrictionLengthInInches": "LONG",
            "RestrictionType": "SHORT",
            "RestrictionWeightInPounds": "LONG",
            "RestrictionWidthInInches": "LONG",
            "SAMaxAxle": "LONG",

            "State": "TEXT",
            "StateRouteID": "TEXT",
            "TDMaxAxle": "LONG",
            "VehicleType": "TEXT"
        },
        "domains": {
            "RestrictionType": "CommercialVehicleRestrictionType",
            "IsDetourAvailable": "Boolean",
            "IsExceptionsAllowed": "Boolean",
            "IsPermanentRestriction": "Boolean",
            "IsWarning": "Boolean",
        }
    },
    "HighwayAlerts": {
        "fields": {
            "AlertID": "LONG",
            "County": "TEXT",

            "EndRoadwayLocationDescription": "TEXT",
            "EndRoadwayLocationDirection": "TEXT",
            "EndRoadwayLocationLatitude": "DOUBLE",
            "EndRoadwayLocationLongitude": "DOUBLE",
            "EndRoadwayLocationMilePost": "FLOAT",
            "EndRoadwayLocationRoadName": "TEXT",

            "StartTime": "DATE",
            "EndTime": "DATE",
            "EventCategory": "TEXT",
            "EventStatus": "TEXT",
            "ExtendedDescription": {
                "field_type": "TEXT",
                "field_length": 1500
            },
            "HeadlineDescription": {
                "field_type": "TEXT",
                "field_length": 500
            },
            "LastUpdatedTime": "DATE",
            "Priority": {
                "field_type": "TEXT",
                "field_length": 7
            },
            "Region": "TEXT",
            "StartRoadwayLocationDescription": "TEXT",
            "StartRoadwayLocationDirection": "TEXT",
            "StartRoadwayLocationLatitude": "DOUBLE",
            "StartRoadwayLocationLongitude": "DOUBLE",
            "StartRoadwayLocationMilePost": "FLOAT",
            "StartRoadwayLocationRoadName": "TEXT"
        }
    },
    "HighwayCameras": {
        "geometryType": "POINT",
        "fields": {
            "CameraID": "LONG",
            "LocationDescription": "TEXT",
            "Direction": "TEXT",
            "Latitude": "DOUBLE",
            "Longitude": "DOUBLE",
            "MilePost": "DOUBLE",
            "RoadName": "TEXT",
            "CameraOwner": "TEXT",
            "Description": "TEXT",
            "DisplayLatitude": "DOUBLE",
            "DisplayLongitude": "DOUBLE",
            "ImageHeight": "SHORT",
            "ImageURL": {
                "field_name": "ImageUrl",
                "field_type": "TEXT",
                "field_alias": "Image URL"
            },
            "ImageWidth": "SHORT",
            "IsActive": "SHORT",
            "OwnerURL": {
                "field_name": "OwnerUrl",
                "field_type": "TEXT",
                "field_alias": "Owner URL"
            },
            "Region": "TEXT",
            "SortOrder": "SHORT",
            "Title": "TEXT"
        }
    },
    "MountainPassConditions": {
        "geometryType": "POINT",
        "fields": {
            "DateUpdated": "DATE",
            "ElevationInFeet": "LONG",
            "Latitude": "DOUBLE",
            "Longitude": "DOUBLE",
            "MountainPassId": "LONG",
            "MountainPassName": "TEXT",
            "RestrictionOneRestrictionText": "TEXT",
            "RestrictionOneTravelDirection": "TEXT",
            "RestrictionTwoRestrictionText": "TEXT",
            "RestrictionTwoTravelDirection": "TEXT",
            "RoadCondition": "TEXT",
            "TemperatureInFahrenheit": "SHORT",
            "TravelAdvisoryActive": "SHORT",
            "WeatherCondition": "TEXT"
        },
        "domains": {
            "TravelAdvisoryActive": "Boolean"
        }
    },
    "TollRates": {
        "geometryType": "POINT",
        "fields": {
            "SignName": "TEXT",
            "TripName": "TEXT",
            "CurrentToll": "SHORT",
            "CurrentMessage": "TEXT",
            "StateRoute": "TEXT",
            "TravelDirection": "TEXT",
            "StartMilepost": "SINGLE",
            "StartLocationName": "TEXT",
            "StartLatitude": "DOUBLE",
            "StartLongitude": "DOUBLE",
            "EndMilepost": "SINGLE",
            "EndLocationName": "TEXT",
            "EndLatitude": "DOUBLE",
            "EndLongitude": "DOUBLE"
        }
    },
    "TrafficFlow": {
        "geometryType": "POINT",
        "fields": {
            "FlowDataID": "LONG",
            "FlowReadingValue": "SHORT",
            "LocationDescription": "TEXT",
            "Direction": "TEXT",
            "Latitude": "DOUBLE",
            "Longitude": "DOUBLE",
            "MilePost": "FLOAT",
            "RoadName": "TEXT",
            "Region": "TEXT",
            "StationName": "TEXT",
            "Time": "DATE"
        },
        "domains": {
            "FlowReadingValue": "FlowReadingValues"
        }
    },
    "TravelTimes": {
        "fields": {
            "AverageTime": "LONG",
            "CurrentTime": "LONG",
            "Description": "TEXT",
            "Distance": "DOUBLE",
            "StartPointDescription": "TEXT",
            "StartPointDirection": "TEXT",
            "StartPointLatitude": "DOUBLE",
            "StartPointLongitude": "DOUBLE",
            "StartPointMilePost": "FLOAT",
            "StartPointRoadName": "TEXT",
            "EndPointDescription": "TEXT",
            "EndPointDirection": "TEXT",
            "EndPointLatitude": "DOUBLE",
            "EndPointLongitude": "DOUBLE",
            "EndPointMilePost": "FLOAT",
            "EndPointRoadName": "TEXT",
            "Name": "TEXT",
            "TimeUpdated": "DATE",
            "TravelTimeID": "LONG"
        }
    },
    "WeatherInformation": {
        "geometryType": "POINT",
        "fields": {
            "StationID": "LONG",
            "StationName": "TEXT",
            "Latitude": "DOUBLE",
            "Longitude": "DOUBLE",
            "ReadingTime": "DATE",
            "TemperatureInFahrenheit": "DOUBLE",
            "PrecipitationInInches": "DOUBLE",
            "WindSpeedInMPH": "DOUBLE",
            "WindGustSpeedInMPH": "DOUBLE",
            "Visibility": "SHORT",
            "SkyCoverage": "TEXT",
            "BarometricPressure": "DOUBLE",
            "RelativeHumidity": "DOUBLE",
            "WindDirectionCardinal": {
                "field_type": "TEXT",
                "field_length": 3
            },
            "WindDirection": "DOUBLE"
        }
    },
    "WeatherStations": {
        "geometryType": "POINT",
        "fields": {
            "StationCode": "LONG",
            "StationName": "TEXT",
            "Latitude": "DOUBLE",
            "Longitude": "DOUBLE"
        }
    }
}


def create_table(table_path, table_def_dict=None, data_list=None,
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
        A list of data returned from travelerinfo.get_traveler_info that will
        be used to populate the table.
    templatesWorkspace : str, optional
        The path to a geodatabase containing template tables.  This will be
        faster than using the AddField tool.
    """
    table_name = os.path.split(table_path)[1]

    if table_def_dict is None:
        table_def_dict = TABLE_DEFS_DICT_DICT[table_name]
    field_dict = table_def_dict["fields"]
    is_point = ("geometryType" in table_def_dict and
                table_def_dict["geometryType"] == "POINT" and
                "Longitude" in field_dict and "Latitude" in field_dict)

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
            arcpy.AddMessage("Creating table %s using template %s..." %
                             (table_path, template_path))
            if is_point:
                arcpy.management.CreateFeatureclass(
                    workspace, fc_name, "POINT", template_path,
                    "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", template_path)
            else:
                arcpy.management.CreateTable(
                    workspace, fc_name, template=template_path)
        else:
            arcpy.AddMessage("Creating table %s..." % table_path)
            arcpy.AddWarning(
                "Creating table without a template.  Table creation would be \
faster if using a template.")
            if is_point:
                arcpy.management.CreateFeatureclass(
                    workspace, fc_name, "POINT",
                    spatial_reference=arcpy.SpatialReference(4326))
            else:
                arcpy.management.CreateTable(workspace, fc_name)

            arcpy.AddMessage("Adding fields...")

            _add_fields(field_dict, is_point, table_path)
            _add_domains(table_def_dict, table_path)

    else:
        arcpy.AddMessage("Truncating table %s..." % table_path)
        # Truncate the table if it already exists
        arcpy.management.DeleteRows(table_path)

    if data_list is not None:
        bad_value_re = re.compile(r"^(?P<error>.+) \[(?P<field>\w+)\]$",
                                  re.MULTILINE)
        arcpy.AddMessage("Adding data to table...")
        fields = list(field_dict.keys())
        if is_point:
            map(fields.remove, ("Longitude", "Latitude"))
            fields.append("SHAPE@XY")
        with arcpy.da.InsertCursor(table_path, fields) as cursor:
            for item in data_list:
                row = []
                for key in fields:
                    if (key == "SHAPE@XY" and "Longitude" in item and
                            "Latitude" in item):
                        x, y = item["Longitude"], item["Latitude"]
                        if x == 0 or y == 0 or x is None or y is None:
                            arcpy.AddWarning("Invalid coordinates. Setting to \
NULL.\n%s" % json.dumps(item, cls=CustomEncoder, indent=4))
                            row.append(None)
                        else:
                            row.append((x, y))
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
                    if err_inst.args:
                        msg_template = "Bad value in [%s] field.\nLength is \
%s.\nValue is %s\n%s"
                        for arg in err_inst.args:
                            matches = bad_value_re.findall(arg)
                            # [(u'The row contains a bad value.',
                            # u'CVRestrictions'), (u'The row contains a bad
                            # value.', u'RestrictionComment')]
                            for match in matches:
                                error_msg, field_name = match
                                if field_name != table_name:
                                    arcpy.AddWarning(msg_template % (
                                        field_name, len(item[field_name]),
                                        item[field_name], error_msg))
                                else:
                                    pass
                    else:
                        arcpy.AddWarning("Error adding row to table.\n%s\n%s" %
                                         (err_inst, item))


def _add_fields(field_dict, is_point, table_path):
    """Adds fields to a table
    """
    skipped_fields_re = re.compile(r"^L((ong)|(at))itude$", re.VERBOSE)

    # Add the columns
    for key in field_dict:
        if is_point and skipped_fields_re.match(key):
            # Don't add Long. or Lat. fields. These will be added as
            # SHAPE@XY.
            continue
        val = field_dict[key]
        if isinstance(val, dict):
            if "field_name" not in val:
                val["field_name"] = key
            if "field_alias" not in val:
                val["field_alias"] = parseutils.split_camel_case(
                    val["field_name"])
            arcpy.management.AddField(table_path, **val)
        else:
            arcpy.management.AddField(table_path, key, val,
                                      field_alias=parseutils.
                                      split_camel_case(key))


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

    for field_name, domain_name in domain_dict.iteritems():
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


if __name__ == '__main__':
    # Get the parameters or set default values.
    ARG_COUNT = arcpy.GetArgumentCount()
    OUT_PATH = "./TravelerInfo.gdb"
    if ARG_COUNT > 0:
        OUT_PATH = arcpy.GetParameterAsText(0)
    ACCESS_CODE = None
    if ARG_COUNT > 1:
        ACCESS_CODE = arcpy.GetParameterAsText(1)
    TEMPLATES_GDB = "Data/Templates.gdb"
    if ARG_COUNT > 2:
        TEMPLATES_GDB = arcpy.GetParameterAsText(2)
    if not arcpy.Exists(TEMPLATES_GDB):
        TEMPLATES_GDB = None

    # Create the file GDB if it does not already exist.
    arcpy.env.overwriteOutput = True
    if not arcpy.Exists(OUT_PATH):
        arcpy.management.CreateFileGDB(*os.path.split(OUT_PATH))

    # Download each of the REST endpoints.
    for name in URLS:
        arcpy.AddMessage("Contacting %s..." % URLS[name])
        if ACCESS_CODE:
            data = travelerinfo.get_traveler_info(name, ACCESS_CODE)
        else:
            data = travelerinfo.get_traveler_info(name)
        OUT_TABLE = os.path.join(OUT_PATH, name)
        create_table(OUT_TABLE, None, data, TEMPLATES_GDB)
    arcpy.SetParameterAsText(3, OUT_PATH)
