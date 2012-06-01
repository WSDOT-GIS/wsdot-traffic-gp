'''travelerinfogp
Queries the WSDOT Traveler Info REST endpoints and populates a table using the results.
@author: Jeff Jacobson

Parameters:
0	URL
1	Workspace
2	Table (output)
'''
import sys, os, re, datetime, parseutils, travelerinfo, arcpy

#urls = {
#	"Border Crossings": "http://www.wsdot.wa.gov/Traffic/api/BorderCrossings/BorderCrossingsREST.svc/GetBorderCrossingsAsJson", 
#	"Highway Alerts": "http://www.wsdot.wa.gov/Traffic/api/HighwayAlerts/HighwayAlertsREST.svc/GetAlertsAsJson",
#	"CV Restrictions": "http://www.wsdot.wa.gov/Traffic/api/CVRestrictions/CVRestrictionsREST.svc/GetCommercialVehicleRestrictionsAsJson",
#	"Cameras": "http://www.wsdot.wa.gov/Traffic/api/HighwayCameras/HighwayCamerasREST.svc/GetCamerasAsJson",
#	"MountainPassConditions": "Service at http://www.wsdot.wa.gov/Traffic/api/MountainPassConditions/MountainPassConditionsREST.svc/GetMountainPassConditionsAsJson",
#	"Traffic Flow": "http://www.wsdot.wa.gov/Traffic/api/TrafficFlow/TrafficFlowREST.svc/GetTrafficFlowsAsJson",
#	"Travel Times": "http://www.wsdot.wa.gov/Traffic/api/TravelTimes/TravelTimesREST.svc/GetTravelTimesAsJson"
#	}

# This dictionary defines the fields in each table.  Each field's dictionary entry can either contain a single string value 
# indicating the field type, or a dictionary with parameters for the arcpy.management.AddField function 
# (excluding in_table and field_name, which are already provided by the dictionary keys).
fieldsDict = {
			"BorderCrossings": {
							"BorderCrossingLocationDescription": "TEXT",
							"BorderCrossingLocationDirection": "TEXT",
							"BorderCrossingLocationLatitude": "DOUBLE",
							"BorderCrossingLocationLongitude": "DOUBLE",
							"BorderCrossingLocationMilePost": "SINGLE",
							"BorderCrossingLocationRoadName": "TEXT"
							},
			"CVRestrictions": {
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
							"RestrictionComment":"TEXT",
							"RestrictionHeightInInches":"LONG",
							"RestrictionLengthInInches":"LONG",
							"RestrictionType":"SHORT", # "BridgeRestriction" or "RoadRestriction"
							"RestrictionWeightInPounds":"LONG",
							"RestrictionWidthInInches":"LONG",
							"SAMaxAxle":"LONG",

							"State":"TEXT",
							"StateRouteID":"TEXT",
							"TDMaxAxle":"LONG",
							"VehicleType":"TEXT",
			},
			"HighwayAlerts": {
				"AlertID": "LONG",
				"County": "TEXT",
				
				"EndRoadwayLocationDescription": "TEXT",
				"EndRoadwayLocationDirection": "TEXT",
				"EndRoadwayLocationLatitude": "DOUBLE",
				"EndRoadwayLocationLongitude": "DOUBLE",
				"EndRoadwayLocationMilePost": "FLOAT",
				"EndRoadwayLocationRoadName": "TEXT",
		
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
			},
			"HighwayCameras": {
				"CameraID":"LONG",
				"CameraLocationDescription":"TEXT",
				"CameraLocationDirection":"TEXT",
				"CameraLocationLatitude":"DOUBLE",
				"CameraLocationLongitude":"DOUBLE",
				"CameraLocationMilePost":"DOUBLE",
				"CameraLocationRoadName":"TEXT",
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
			},
			"MountainPassConditions": {
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
			},
			"TrafficFlow": {
				"FlowDataID":"LONG",
				"FlowReadingValue":"SHORT",
				"FlowStationLocationDescription":"TEXT",
				"FlowStationLocationDirection":"TEXT",
				"FlowStationLocationLatitude":"DOUBLE",
				"FlowStationLocationLongitude":"DOUBLE",
				"FlowStationLocationMilePost":"FLOAT",
				"FlowStationLocationRoadName":"TEXT",
				"Region":"TEXT",
				"StationName":"TEXT",
				"Time":"DATE"
			},
			"TravelTimes": {
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
		}


def createTable(tablePath, fieldDict=None, dataList=None):
	"""Creates a table 
	"""
	# Create the table if it does not already exist.
	if not arcpy.Exists(tablePath):
		# Check to see if the fieldDict parameter was provided.  If not, get the fields from the fieldsDict based on 
		# the table name in tablePath.
		if fieldDict is None:
			tableName = os.path.split(tablePath)[1]
			fieldDict = fieldsDict[tableName]

		arcpy.AddMessage("Creating table \"%s\"" % tablePath)
		# Create the table.
		arcpy.management.CreateTable(*os.path.split(tablePath))
		
		arcpy.AddMessage("Adding fields...")
		# Add the columns
		for key in fieldDict:
			try:
				val = fieldDict[key]
				if (type(val) == dict):
					val["field_alias"] = parseutils.splitCamelCase(key)
					arcpy.management.AddField(tablePath, key, **val)
				else:
					arcpy.management.AddField(tablePath, key, val, field_alias = parseutils.splitCamelCase(key))
			except Exception as err:
				arcpy.AddError(err)

		arcpy.management.AddField(tablePath, "StartTime", "DATE")
	else:
		arcpy.AddMessage("Truncating table %s..." % tablePath)
		# Truncate the table if it already exists
		arcpy.management.DeleteRows(tablePath)
	
	if (dataList is not None):
		arcpy.AddMessage("Adding data to table...")
		cursor = arcpy.InsertCursor(tablePath)
		row = None
		try:
			for item in dataList:
				row = cursor.newRow()
				for key in item:
					val = item[key]
					if val is not None:
						if isinstance(val, datetime.datetime):
							row.setValue(key, str(val))
						elif isinstance(val, bool):
							if val:
								row.setValue(key, 1)
							else:
								row.setValue(key, 0)
						else:
							row.setValue(key, item[key])
				cursor.insertRow(row)
		except:
			arcpy.AddError("Error adding item to table.\n%s" % item)
			raise
		finally:
			del row, cursor

def createAlertsTable(tablePath, alertList):
	createTable(tablePath, fieldsDict["HighwayAlerts"], alertList)

def getDefaultTableName(url):
	"""Extracts a table name from the URL.
	"""
	#urls = {
#	"Border Crossings": "http://www.wsdot.wa.gov/Traffic/api/BorderCrossings/BorderCrossingsREST.svc/GetBorderCrossingsAsJson", 
#	"Highway Alerts": "http://www.wsdot.wa.gov/Traffic/api/HighwayAlerts/HighwayAlertsREST.svc/GetAlertsAsJson",
#	"CV Restrictions": "http://www.wsdot.wa.gov/Traffic/api/CVRestrictions/CVRestrictionsREST.svc/GetCommercialVehicleRestrictionsAsJson",
#	"Cameras": "http://www.wsdot.wa.gov/Traffic/api/HighwayCameras/HighwayCamerasREST.svc/GetCamerasAsJson",
#	"MountainPassConditions": "Service at http://www.wsdot.wa.gov/Traffic/api/MountainPassConditions/MountainPassConditionsREST.svc/GetMountainPassConditionsAsJson",
#	"Traffic Flow": "http://www.wsdot.wa.gov/Traffic/api/TrafficFlow/TrafficFlowREST.svc/GetTrafficFlowsAsJson",
#	"Travel Times": "http://www.wsdot.wa.gov/Traffic/api/TravelTimes/TravelTimesREST.svc/GetTravelTimesAsJson"
#	}

	names = ["BorderCrossings", "HighwayAlerts", "CVRestrictions", "HighwayCameras", "MountainPassConditions", 
			"TrafficFlow", "TravelTimes"]
	for name in names:
		if re.search(name, url, re.IGNORECASE):
			return name
	raise "Unsupported URL format"

if __name__ == '__main__':
	argCount = arcpy.GetArgumentCount()
	if argCount < 1:
		arcpy.AddError("You must specify your traveler api URL (including access code).")
	
	else:
		# Get the URL
		url = arcpy.GetParameterAsText(0)
		
		# Get the workspace path
		if argCount > 1:
			workspace = arcpy.GetParameterAsText(1)
		else:
			# get the root directory
			dirName = os.path.dirname(os.path.dirname(sys.argv[0]))
			workspace = os.path.join(dirName, "Scratch", "Scratch.gdb")
		arcpy.AddMessage("Workspace is %s." % workspace)
			
		# Throw an error if the workspace does not exist
		if not arcpy.Exists(workspace):
			arcpy.AddError("Workspace does not exist: \"%s\"." % workspace)
			
		# Get the table name
		tableName = getDefaultTableName(url)
			
		travelerInfo = travelerinfo.getTravelerInfo(url)
				
		tablePath = os.path.join(workspace, tableName)
		
		if tableName == "HighwayAlerts":
			createAlertsTable(tablePath, travelerInfo)
		else:
			raise NotImplementedError()
		
		arcpy.SetParameterAsText(2, tablePath)