'''travelerinfo
Returns data from the WSDOT Traveler Info REST endpoints. 
@author: Jeff Jacobson

Parameters:
1	REST URL
'''
import sys, urllib2, json, parseutils

def parseTravelerInfoObject(dct):
	"""This method is used by the json.load method to customize how the alerts are deserialized.
	@type dct: dict 
	"""
	output = {}
	for key in dct:
		val = dct[key]
		if isinstance(val, dict):
			# Roadway locations will be "flattened", since tables can't have nested values.
			for rlKey in val:
				output[key + rlKey] = val[rlKey]
		elif isinstance(val, (str, unicode)):
			# Parse date/time values.
			output[key] = parseutils.parseDate(val) # Either parses into date (if possible) or returns the original string.
		else:
			output[key] = dct[key]
	return output

def getTravelerInfoJson(url):
	"""Gets the highway alerts data from the REST endpoint.
	@param url: The URL to the REST Endpoint that will provide the data, including the "accessCode" query string parameter.
	@type url: str
	@return: The JSON output from the rest endpoint
	@rtype: list
	"""
	f = urllib2.urlopen(url)
	output = f.read()
	del f
	return output

def getTravelerInfo(url):
	"""Gets the highway alerts data from the REST endpoint.
	@param url: The URL to the REST Endpoint that will provide the data, including the "accessCode" query string parameter.
	@type url: str
	@return: Returns a list of dict objects.
	@rtype: list
	"""
	f = urllib2.urlopen(url)
	jsonData = json.load(f, object_hook=parseTravelerInfoObject)
	del f
	return jsonData


if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.exit("""You must provide the REST endpoint URL as a parameter.
		%s http://www.wsdot.wa.gov/Traffic/api/HighwayAlerts/HighwayAlertsREST.svc/GetAlertsAsJson?accessCode=your-access-code""" % sys.argv[0])
	else:
		url = sys.argv[1]
		print getTravelerInfoJson(url)