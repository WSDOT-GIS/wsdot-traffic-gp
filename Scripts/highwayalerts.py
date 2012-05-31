'''Highway Alerts
Queries the WSDOT Highway Alerts REST endpoint and populates a table using the results.
@author: Jeff Jacobson

Parameters:
0	Traveler API Access Code
1	Table Path
'''
import sys, os, datetime, urllib2, json, re, arcpy

url = "http://www.wsdot.wa.gov/Traffic/api/HighwayAlerts/HighwayAlertsREST.svc/GetAlertsAsJson?accessCode="

proj = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433],AUTHORITY["EPSG",4326]]'

dateRe = re.compile(r"\/Date\((\d+)([+\-]\d+)\)\/",re.IGNORECASE)

camelCaseRe = re.compile(r"(?:[A-Z][a-z]+)|[A-Z]{2}")

def parseDate(wcfDate):
	"""Parses a WCF serialzied date to a date string.
	@param wcfDate: A date/time in WCF JSON serialized format.
	@type wcfDate: str
	@rtype: datetime.datetime
	"""
	if wcfDate:
		match = dateRe.match(wcfDate)
		if match:
			groups = match.groups()
			ticks = None 
			if (len(groups) >= 2):
				ticks = (int(groups[0]) + int(groups[1])) / 1000
			else:
				ticks = int(groups[0]) / 1000
			return datetime.datetime.fromtimestamp(ticks)
		else:
			return wcfDate

def splitCamelCase(s):
	"""Splits a camel case word into individual words separated by spaces
	@param s: A camel-case word.
	@type s: str
	@rtype: str
	"""
	if (s is not None):
		words = camelCaseRe.findall(s)
		return str.join(" ", words)
	

def parseAlert(dct):
	"""This method is used by the json.load method to customized how the alerts are deserialized.
	@type dct: dict 
	"""
	timeRe = re.compile("(?:Time)|(?:Date)", re.IGNORECASE)
	rlocRe = re.compile("\w+RoadwayLocation", re.IGNORECASE)
	output = {}
	for key in dct:
		if rlocRe.match(key) and dct[key] is not None:
			# Roadway locations will be "flattened", since tables can't have nested values.
			for rlKey in dct[key]:
				output[key + rlKey] = dct[key][rlKey]
			pass
		elif timeRe.search(key):
			# Parse date/time values.
			output[key] = parseDate(dct[key])
			pass
		else:
			output[key] = dct[key]
	return output

def getAlerts(accessCode):
	"""Gets the highway alerts data from the REST endpoint.
	@param accessCode: Access code string.  You get this code from the Traveler API home page.
	@type accessCode: str
	@rtype: list
	"""
	f = urllib2.urlopen(url + accessCode)
	jsonData = json.load(f, object_hook=parseAlert)
	del f
	return jsonData

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
					val["field_alias"] = splitCamelCase(key)
					arcpy.management.AddField(tablePath, key, **val)
				else:
					arcpy.management.AddField(tablePath, key, val, field_alias = splitCamelCase(key))
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

if __name__ == '__main__':
	if arcpy.GetArgumentCount() < 1:
		arcpy.AddError("You must specify your traveler api access code.")
	else:
		accessCode = arcpy.GetParameterAsText(0)
		# accessCode = sys.argv[1]
		alerts = getAlerts(accessCode)
		gdbPath = os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), "Scratch", "Scratch.gdb")
		tablePath = os.path.join(gdbPath, "Alerts")
		if arcpy.Exists(tablePath):
			arcpy.management.Delete(tablePath)
		createAlertsTable(tablePath, alerts)