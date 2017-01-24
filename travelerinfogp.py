'''travelerinfogp
Queries the WSDOT Traveler Info REST endpoints and populates a table using the results.
@author: Jeff Jacobson

Parameters:
0    Endpoint Name. valid values are: BorderCrossings, HighwayAlerts, CVRestrictions, HighwayCameras, MountainPassConditions, TrafficFlow, TravelTimes)
1    Access Code
2    Workspace.  Optional.  Defaults to "../Scratch/Scratch.gdb".
3    Table (output)
'''
import sys, os, datetime, re, parseutils, travelerinfo, arcpy
from resturls import urls

# point_table_names = (
#     "BorderCrossings",
#     "HighwayCameras",
#     "MountainPassConditions",
#     "TrafficFlow",
#     "WeatherInformation",
#     "WeatherStations"
# )

# This dictionary defines the fields in each table.  Each field's dictionary entry can either contain a single string value
# indicating the field type, or a dictionary with parameters for the arcpy.management.AddField function
# (excluding in_table and field_name, which are already provided by the dictionary keys).
fieldsDict = {
    "BorderCrossings": {
        "geometryType": "POINT",
        "fields": {
            "Description": "TEXT",
            "Direction": "TEXT",
            "Latitude": "DOUBLE",
            "Longitude": "DOUBLE",
            "MilePost": "SINGLE",
            "RoadName": "TEXT",
            "CrossingName":"TEXT",
            "Time":"DATE",
            "WaitTime":"SHORT"
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
        }
    },
    "CVRestrictions": {
        "fields": {
            "BLMaxAxle":"LONG",
            "BridgeName":"TEXT",
            "BridgeNumber":"TEXT",
            "CL8MaxAxle":"LONG",
            "DateEffective":"DATE",
            "DateExpires":"DATE",
            "DatePosted":"DATE",

            "StartRoadwayLocationDescription":"TEXT",
            "StartRoadwayLocationDirection":"TEXT",
            "StartRoadwayLocationLatitude":"DOUBLE",
            "StartRoadwayLocationLongitude":"DOUBLE",
            "StartRoadwayLocationMilePost":"SINGLE",
            "StartRoadwayLocationRoadName":"TEXT",

            "EndRoadwayLocationDescription":"TEXT",
            "EndRoadwayLocationDirection":"TEXT",
            "EndRoadwayLocationLatitude":"DOUBLE",
            "EndRoadwayLocationLongitude":"DOUBLE",
            "EndRoadwayLocationMilePost":"SINGLE",
            "EndRoadwayLocationRoadName":"TEXT",

            "IsDetourAvailable":"SHORT",
            "IsExceptionsAllowed":"SHORT",
            "IsPermanentRestriction":"SHORT",
            "IsWarning":"SHORT",

            "Latitude":"DOUBLE",
            "Longitude":"DOUBLE",
            "LocationDescription":"TEXT",
            "LocationName":"TEXT",
            "MaximumGrossVehicleWeightInPounds":"LONG",
            "RestrictionComment": {
                                "field_type": "TEXT",
                                "field_length": 800
                                },
            "RestrictionHeightInInches":"LONG",
            "RestrictionLengthInInches":"LONG",
            "RestrictionType":"SHORT", # "BridgeRestriction" or "RoadRestriction"
            "RestrictionWeightInPounds":"LONG",
            "RestrictionWidthInInches":"LONG",
            "SAMaxAxle":"LONG",

            "State":"TEXT",
            "StateRouteID":"TEXT",
            "TDMaxAxle":"LONG",
            "VehicleType":"TEXT"
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
                "field_type":"TEXT",
                "field_length": 1500
            },
            "HeadlineDescription": {
                "field_type":"TEXT",
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
            "CameraID":"LONG",
            "Description":"TEXT",
            "Direction":"TEXT",
            "Latitude":"DOUBLE",
            "Longitude":"DOUBLE",
            "MilePost":"DOUBLE",
            "RoadName":"TEXT",
            "CameraOwner":"TEXT",
            "Description":"TEXT",
            "DisplayLatitude":"DOUBLE",
            "DisplayLongitude":"DOUBLE",
            "ImageHeight":"SHORT",
            "ImageURL":"TEXT",
            "ImageWidth":"SHORT",
            "IsActive":"SHORT",
            "OwnerURL":"TEXT",
            "Region":"TEXT",
            "SortOrder":"SHORT",
            "Title":"TEXT"
        }
    },
    "MountainPassConditions": {
        "geometryType": "POINT",
        "fields": {
            "DateUpdated":"DATE",
            "ElevationInFeet":"LONG",
            "Latitude":"DOUBLE",
            "Longitude":"DOUBLE",
            "MountainPassId":"LONG",
            "MountainPassName":"TEXT",
            "RestrictionOneRestrictionText":"TEXT",
            "RestrictionOneTravelDirection":"TEXT",
            "RestrictionTwoRestrictionText":"TEXT",
            "RestrictionTwoTravelDirection":"TEXT",
            "RoadCondition":"TEXT",
            "TemperatureInFahrenheit":"SHORT",
            "TravelAdvisoryActive":"SHORT",
            "WeatherCondition":"TEXT"
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
            "FlowDataID":"LONG",
            "FlowReadingValue":"SHORT",
            "Description":"TEXT",
            "Direction":"TEXT",
            "Latitude":"DOUBLE",
            "Longitude":"DOUBLE",
            "MilePost":"FLOAT",
            "RoadName":"TEXT",
            "Region":"TEXT",
            "StationName":"TEXT",
            "Time":"DATE"
        }
    },
    "TravelTimes": {
        "fields": {
            "AverageTime":"LONG",
            "CurrentTime":"LONG",
            "Description":"TEXT",
            "Distance":"DOUBLE",
            "StartPointDescription":"TEXT",
            "StartPointDirection":"TEXT",
            "StartPointLatitude":"DOUBLE",
            "StartPointLongitude":"DOUBLE",
            "StartPointMilePost":"FLOAT",
            "StartPointRoadName":"TEXT",
            "EndPointDescription":"TEXT",
            "EndPointDirection":"TEXT",
            "EndPointLatitude":"DOUBLE",
            "EndPointLongitude":"DOUBLE",
            "EndPointMilePost":"FLOAT",
            "EndPointRoadName":"TEXT",
            "Name":"TEXT",
            "TimeUpdated":"DATE",
            "TravelTimeID":"LONG"
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
            "WindDirectionCardinal": "TEXT",
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


def createTable(tablePath, tableDefDict=None, dataList=None, templatesWorkspace=None):
    """Creates a table for one of the Traveler API REST Endpoints' data.
    @param tablePath: The path where the new table will be created. If this path already exists than the existing table will be truncated.
    @type tablePath: str
    @param tableDefDict: Optional. A dict that defines the fields that will be created.  If omitted, the fields will be determined by the table path.
    @type tableDefDict: dict
    @param dataList: Optional. A list of data returned from travelerinfo.getTravelerInfo that will be used to populate the table.
    @type dataList: list
    @param templatesWorkspace: Optional. The path to a geodatabase containing template tables.  This will be faster than using the AddField tool.
    @type templatesWorkspace: str
    """
    tableName = os.path.split(tablePath)[1]

    if tableDefDict is None:
        tableDefDict = fieldsDict[tableName]
    fieldDict = tableDefDict["fields"]
    isPoint = "geometryType" in tableDefDict and tableDefDict["geometryType"] == "POINT" and "Longitude" in fieldDict and "Latitude" in fieldDict

    # Create the table if it does not already exist.
    if not arcpy.Exists(tablePath):
        # Check to see if the fieldDict parameter was provided.  If not, get the fields from the fieldsDict based on
        # the table name in tablePath.
        ws, fcname = os.path.split(tablePath)
        if templatesWorkspace is not None and arcpy.Exists(os.path.join(templatesWorkspace, tableName)):
            templatePath = os.path.join(templatesWorkspace, tableName)
            arcpy.AddMessage("Creating table %s using template %s..." % (tablePath, templatePath))
            if isPoint:
                arcpy.management.CreateFeatureclass(ws, fcname, "POINT", templatePath, "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", templatePath)
            else:
                arcpy.management.CreateTable(ws, fcname, template=templatePath)
        else:
            arcpy.AddMessage("Creating table %s..." % tablePath)
            arcpy.AddWarning("Creating table without a template.  Table creation would be faster if using a template.")
            if isPoint:
                arcpy.management.CreateFeatureclass(ws, fcname, "POINT", spatial_reference=arcpy.SpatialReference(4326))
            else:
                arcpy.management.CreateTable(ws, fcname)

            arcpy.AddMessage("Adding fields...")

            skippedFieldsRe = re.compile(r"^L((ong)|(at))itude$", re.VERBOSE)

            # Add the columns
            for key in fieldDict:
                if isPoint and skippedFieldsRe.match(key):
                    # Don't add Long. or Lat. fields. These will be added as SHAPE@XY.
                    continue
                try:
                    val = fieldDict[key]
                    if (type(val) == dict):
                        if "field_alias" not in val:
                            val["field_alias"] = parseutils.splitCamelCase(key)
                        arcpy.management.AddField(tablePath, key, **val)
                    else:
                        arcpy.management.AddField(tablePath, key, val, field_alias = parseutils.splitCamelCase(key))
                except Exception as err:
                    arcpy.AddError(err)
    else:
        arcpy.AddMessage("Truncating table %s..." % tablePath)
        # Truncate the table if it already exists
        arcpy.management.DeleteRows(tablePath)

    if (dataList is not None):
        badValueRe = re.compile("^(?P<error>.+) \[(?P<field>\w+)\]$",re.MULTILINE)
        arcpy.AddMessage("Adding data to table...")
        fields = list(fieldDict.keys())
        if isPoint:
            map(fields.remove, ("Longitude", "Latitude"))
            fields.append("SHAPE@XY")
        with arcpy.da.InsertCursor(tablePath, fields) as cursor:
            for item in dataList:
                row = []
                for key in fields:
                    if key == "SHAPE@XY" and "Longitude" in item and "Latitude" in item:
                        row.append((item["Longitude"], item["Latitude"]))
                    elif not key in item:
                        row.append(None)
                    else:
                        val = item[key]
                        row.append(val)
                try:
                    cursor.insertRow(row)
                except RuntimeError as errInst:
                    # Sample args value of errInst:
                    # tuple: ('ERROR 999999: Error executing function.\nThe row contains a bad value. [CVRestrictions]\nThe row contains a bad value. [RestrictionComment]',)
                    if errInst.args:
                        for arg in errInst.args:
                            matches = badValueRe.findall(arg) #[(u'The row contains a bad value.', u'CVRestrictions'), (u'The row contains a bad value.', u'RestrictionComment')]
                            for match in matches:
                                errMsg, fieldName = match
                                if fieldName != tableName:
                                    arcpy.AddWarning("Bad value in [%s] field.\nLength is %s.\nValue is %s\n%s" % (fieldName, len(item[fieldName]), item[fieldName], errMsg))
                                    pass
                                else:
                                    pass
                    else:
                        arcpy.AddWarning("Error adding row to table.\n%s\n%s" % (errInst, item))

if __name__ == '__main__':
    argCount = arcpy.GetArgumentCount()
    if argCount < 1:
        arcpy.AddError("You must specify your traveler api type.")

    else:
        # Get the URL
        tableName = arcpy.GetParameterAsText(0)
        if argCount >= 2:
            accessCode = arcpy.GetParameterAsText(1)
        else:
            accessCode = None

        # get the root directory
        dirName = os.path.dirname(os.path.dirname(sys.argv[0]))

        # Get the workspace path
        if argCount > 2:
            workspace = arcpy.GetParameterAsText(2)
        else:
            workspace = arcpy.env.scratchGDB
        arcpy.AddMessage("Workspace is %s." % workspace)

        templatesGdbPath = os.path.join(dirName, "Data", "Templates.gdb")
        if not arcpy.Exists(templatesGdbPath):
            templatesGdbPath = None

        # Throw an error if the workspace does not exist
        if not arcpy.Exists(workspace):
            arcpy.AddError("Workspace does not exist: \"%s\"." % workspace)

        if accessCode is not None:
            travelerInfo = travelerinfo.getTravelerInfo(tableName, accessCode)
        else:
            travelerInfo = travelerinfo.getTravelerInfo(tableName)
        tablePath = os.path.join(workspace, tableName)

        createTable(tablePath, dataList=travelerInfo, templatesWorkspace=templatesGdbPath)

        # Set the table output parameter
        arcpy.SetParameterAsText(3, tablePath)