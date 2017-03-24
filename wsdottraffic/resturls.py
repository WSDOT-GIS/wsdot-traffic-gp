"""
Provides a list of URLs for REST endpoints.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

API_BASE = "http://www.wsdot.wa.gov/Traffic/api"

URLS = {
    "BorderCrossings":
    "%s/BorderCrossings/BorderCrossingsREST.svc/GetBorderCrossingsAsJson" %
    API_BASE,
    "BridgeClearances": "%s/Bridges/ClearanceREST.svc/GetClearancesAsJson" %
                        API_BASE,
    "CVRestrictions":
    "%s/CVRestrictions/CVRestrictionsREST.\
svc/GetCommercialVehicleRestrictionsAsJson" % API_BASE,
    "HighwayAlerts": "%s/HighwayAlerts/HighwayAlertsREST.svc/GetAlertsAsJson" %
                     API_BASE,
    "HighwayCameras":
    "%s/HighwayCameras/HighwayCamerasREST.svc/GetCamerasAsJson" % API_BASE,
    "MountainPassConditions":
    "%s/MountainPassConditions/MountainPassConditionsREST.svc/\
GetMountainPassConditionsAsJson" % API_BASE,
    "TollRates": "%s/api/tolling" % API_BASE,
    "TrafficFlow": "%s/TrafficFlow/TrafficFlowREST.svc/GetTrafficFlowsAsJson" %
                   API_BASE,
    "TravelTimes": "%s/TravelTimes/TravelTimesREST.svc/GetTravelTimesAsJson" %
                   API_BASE,
    "WeatherInformation":
    "%s/WeatherInformation/WeatherInformationREST.\
svc/GetCurrentWeatherInformationAsJson" % API_BASE,
    "WeatherStations":
    "%s/WeatherStations/WeatherStationsREST.svc/GetCurrentStationsAsJson" %
    API_BASE
}

ALERT_EVENT_CATEGORIES_URL = (
    "%s/HighwayAlerts/HighwayAlertsREST.svc/GetEventCategoriesAsJson" %
    API_BASE)
