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

def createAlertsTable(tablePath, alertList):
	if not arcpy.Exists(tablePath):
		arcpy.AddMessage("Creating table \"%s\"" % tablePath)
		# Create the table.
		arcpy.management.CreateTable(*os.path.split(tablePath))
		
		arcpy.AddMessage("Adding fields...")
		# Add the columns

		fieldDict = {
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
		}
		
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
	
	if (alertList is not None):
		arcpy.AddMessage("Adding data to table...")
		cursor = arcpy.InsertCursor(tablePath)
		row = None
		try:
			for alert in alertList:
				row = cursor.newRow()
				for key in alert:
					if alert[key] is not None:
						if isinstance(alert[key], datetime.datetime):
							row.setValue(key, str(alert[key]))
						else:
							row.setValue(key, alert[key])
				cursor.insertRow(row)
		except:
			arcpy.AddError(alert)
			raise
		finally:
			del row, cursor

def getDefaultTableName(url):
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
			
		# Throw an error if the workspace does not exist
		if not arcpy.Exists(workspace):
			arcpy.AddError("Workspace does not exist: \"%s\"." % workspace)
			
		# Get the table name
			
		# accessCode = sys.argv[1]
		tableName = getDefaultTableName(url)
			
		travelerInfo = travelerinfo.getTravelerInfo(url)
				
		tablePath = os.path.join(workspace, tableName)
		
		if tableName == "HighwayAlerts":
			createAlertsTable(tablePath, travelerInfo)
		else:
			raise NotImplementedError()