'''travelerinfogp
Queries the WSDOT Traveler Info REST endpoints and populates a table using the results.
@author: Jeff Jacobson

Parameters:
0	Endpoint Name. valid values are: BorderCrossings, HighwayAlerts, CVRestrictions, HighwayCameras, MountainPassConditions, TrafficFlow, TravelTimes)
1	Access Code
2	Workspace.  Optional.  Defaults to "../Scratch/Scratch.gdb".
3	Table (output)
'''
import sys, os, datetime, re, parseutils, travelerinfo, arcpy

urls = {
	"BorderCrossings": "http://www.wsdot.wa.gov/Traffic/api/BorderCrossings/BorderCrossingsREST.svc/GetBorderCrossingsAsJson", 
	"HighwayAlerts": "http://www.wsdot.wa.gov/Traffic/api/HighwayAlerts/HighwayAlertsREST.svc/GetAlertsAsJson",
	"CVRestrictions": "http://www.wsdot.wa.gov/Traffic/api/CVRestrictions/CVRestrictionsREST.svc/GetCommercialVehicleRestrictionsAsJson",
	"HighwayCameras": "http://www.wsdot.wa.gov/Traffic/api/HighwayCameras/HighwayCamerasREST.svc/GetCamerasAsJson",
	"MountainPassConditions": "Service at http://www.wsdot.wa.gov/Traffic/api/MountainPassConditions/MountainPassConditionsREST.svc/GetMountainPassConditionsAsJson",
	"TrafficFlow": "http://www.wsdot.wa.gov/Traffic/api/TrafficFlow/TrafficFlowREST.svc/GetTrafficFlowsAsJson",
	"TravelTimes": "http://www.wsdot.wa.gov/Traffic/api/TravelTimes/TravelTimesREST.svc/GetTravelTimesAsJson"
	}

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
							"BorderCrossingLocationRoadName": "TEXT",
							"CrossingName":"TEXT",
							"Time":"DATE",
							"WaitTime":"SHORT"
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
							"RestrictionComment": {
												"field_type": "TEXT",
												"field_length": 550
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


def createTable(tablePath, fieldDict=None, dataList=None, templatesWorkspace=None):
	"""Creates a table for one of the Traveler API REST Endpoints' data.
	@param tablePath: The path where the new table will be created. If this path already exists than the existing table will be truncated.
	@type tablePath: str
	@param fieldDict: Optional. A dict that defines the fields that will be created.  If omitted, the fields will be determined by the table path.
	@type fieldDict: dict
	@param dataList: Optional. A list of data returned from travelerinfo.getTravelerInfo that will be used to populate the table.
	@type dataList: list
	@param templatesWorkspace: Optional. The path to a geodatabase containing template tables.  This will be faster than using the AddField tool.
	@type templatesWorkspace: str
	"""
	tableName = os.path.split(tablePath)[1]
	# Create the table if it does not already exist.
	if not arcpy.Exists(tablePath):
		# Check to see if the fieldDict parameter was provided.  If not, get the fields from the fieldsDict based on 
		# the table name in tablePath.
		if fieldDict is None:
			fieldDict = fieldsDict[tableName]

		arcpy.AddMessage("Creating table \"%s\"" % tablePath)
		
		if templatesWorkspace is not None and arcpy.Exists(os.path.join(templatesWorkspace, tableName)):
			templatePath = os.path.join(templatesWorkspace, tableName)
			arcpy.AddMessage("Creating table %s using template %s..." % (tablePath, templatePath))
			arcpy.management.CreateTable(*os.path.split(tablePath), template=templatePath)
		else:
			arcpy.AddMessage("Creating table %s..." % tablePath)
			arcpy.AddWarning("Creating table without a template.  Table creation would be faster if using a template.")
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
	else:
		arcpy.AddMessage("Truncating table %s..." % tablePath)
		# Truncate the table if it already exists
		arcpy.management.DeleteRows(tablePath)
	
	if (dataList is not None):
		badValueRe = re.compile("^(?P<error>.+) \[(?P<field>\w+)\]$",re.MULTILINE)
		arcpy.AddMessage("Adding data to table...")
		cursor = arcpy.InsertCursor(tablePath)
		row = None
		try:
			for item in dataList:
				row = cursor.newRow()
				for key in item:
					val = item[key]
					if val is not None:
						try:
							if isinstance(val, datetime.datetime):
								row.setValue(key, str(val))
							elif isinstance(val, bool):
								if val:
									row.setValue(key, 1)
								else:
									row.setValue(key, 0)
							else:
								row.setValue(key, val)
						except (ValueError, RuntimeError) as errInst:
							arcpy.AddWarning("Error adding value %s to field %s.\n%s" % (val, key, errInst))
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
		except Exception as errInst:
			arcpy.AddWarning("Error adding row to table.\n%s\n%s" % (errInst, item))
			raise
		finally:
			del row, cursor

if __name__ == '__main__':
	argCount = arcpy.GetArgumentCount()
	if argCount < 1:
		arcpy.AddError("You must specify your traveler api URL (including access code).")
	
	else:
		# Get the URL
		tableName = arcpy.GetParameterAsText(0)
		accessCode = arcpy.GetParameterAsText(1)
		url = "%s?accessCode=%s" % (urls[tableName], accessCode)
		
		# get the root directory
		dirName = os.path.dirname(os.path.dirname(sys.argv[0]))
		
		# Get the workspace path
		if argCount > 2:
			workspace = arcpy.GetParameterAsText(2)
		else:
			workspace = os.path.join(dirName, "Scratch", "Scratch.gdb")
		arcpy.AddMessage("Workspace is %s." % workspace)
		
		templatesGdbPath = os.path.join(dirName, "Data", "Templates.gdb")
		if not arcpy.Exists(templatesGdbPath):
			templatesGdbPath = None
			
		# Throw an error if the workspace does not exist
		if not arcpy.Exists(workspace):
			arcpy.AddError("Workspace does not exist: \"%s\"." % workspace)
			
		travelerInfo = travelerinfo.getTravelerInfo(url)
				
		tablePath = os.path.join(workspace, tableName)
		
		createTable(tablePath, dataList=travelerInfo, templatesWorkspace=templatesGdbPath)
		
		# Set the table output parameter
		arcpy.SetParameterAsText(3, tablePath)