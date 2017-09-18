"""This module is for the Scanweb REST endpoint
"""

from __future__ import unicode_literals, print_function, absolute_import, division
from sys import stderr
import requests
from ..resturls import URLS
from .. import _DEFAULT_ACCESS_CODE

# pylint: disable=invalid-name,too-few-public-methods

class SurfaceMeasurements(object):
    """
    byte 	SensorId [get, set]
    decimal 	SurfaceTemperature [get, set]
    decimal 	RoadFreezingTemperature [get, set]
    int 	RoadSurfaceCondition [get, set]
    """
    def __init__(self, **kwargs):
        self.SensorId = kwargs.get("SensorId")
        self.SurfaceTemperature = kwargs.get("SurfaceTemperature")
        self.RoadFreezingTemperature = kwargs.get("RoadFreezingTemperature")
        self.RoadSurfaceCondition = kwargs.get("RoadSurfaceCondition")


class SubSurfaceMeasurements(object):
    """
    byte 	SensorId [get, set]
    decimal 	SubSurfaceTemperature [get, set]
    """
    def __init__(self, **kwargs):
        self.SensorId = kwargs.get("SensorId")
        self.SubSurfaceTemperature = kwargs.get("SubSurfaceTemperature")


class WeatherReading(object):
    """
    string 	StationId [get, set]

    string 	StationName [get, set]

    decimal 	Latitude [get, set]

    decimal 	Longitude [get, set]

    int 	Elevation [get, set]

    DateTime 	ReadingTime [get, set]

    decimal 	AirTemperature [get, set]

    byte 	RelativeHumidty [get, set]

    byte 	AverageWindSpeed [get, set]

    short 	AverageWindDirection [get, set]

    byte 	WindGust [get, set]

    short 	Visibility [get, set]

    byte 	PrecipitationIntensity [get, set]

    byte 	PrecipitationType [get, set]

    decimal 	PrecipitationPast1Hour [get, set]

    decimal 	PrecipitationPast3Hours [get, set]

    decimal 	PrecipitationPast6Hours [get, set]

    decimal 	PrecipitationPast12Hours [get, set]

    decimal 	PrecipitationPast24Hours [get, set]

    decimal 	PrecipitationAccumulation [get, set]

    int 	BarometricPressure [get, set]

    int 	SnowDepth [get, set]

    List< ScanwebSurfaceMeasurements > 	SurfaceMeasurements [get, set]

    List< ScanwebSubSurfaceMeasurements > 	SubSurfaceMeasurements [get, set]
    """

    @property
    def ScanwebSurfaceMeasurements(self):
        return self._ScanwebSurfaceMeasurements

    @property
    def ScanwebSubSurfaceMeasurements(self):
        return self._ScanwebSubSurfaceMeasurements

    def __init__(self, **kwargs):
        self.StationId = kwargs.get("StationId")
        self.StationName = kwargs.get("StationName")
        self.Latitude = kwargs.get("Latitude")
        self.Longitude = kwargs.get("Longitude")
        self.Elevation = kwargs.get("Elevation")
        self.ReadingTime = kwargs.get("ReadingTime")
        self.AirTemperature = kwargs.get("AirTemperature")
        self.RelativeHumidity = kwargs.get("RelativeHumidty")
        self.AverageWindSpeed = kwargs.get("AverageWindSpeed")
        self.AverageWindDirection = kwargs.get("AverageWindDirection")
        self.WindGust = kwargs.get("WindGust")
        self.Visibility = kwargs.get("Visibility")
        self.PrecipitationIntensity = kwargs.get("PrecipitationIntensity")
        self.PrecipitationType = kwargs.get("PrecipitationType")
        self.PrecipitationPast1Hour = kwargs.get("PrecipitationPast1Hour")
        self.PrecipitationPast3Hours = kwargs.get("PrecipitationPast3Hours")
        self.PrecipitationPast6Hours = kwargs.get("PrecipitationPast6Hours")
        self.PrecipitationPast12Hours = kwargs.get("PrecipitationPast12Hours")
        self.PrecipitationPast24Hours = kwargs.get("PrecipitationPast24Hours")
        self.PrecipitationAccumulation = kwargs.get("PrecipitationAccumulation")
        self.BarometricPressure = kwargs.get("BarometricPressure")
        self.SnowDepth = kwargs.get("SnowDepth")
        self._ScanwebSurfaceMeasurements = []
        self._ScanwebSubSurfaceMeasurements = []

        measure_list = kwargs.get("ScanwebSurfaceMeasurements")
        if measure_list:
            for item in measure_list:
                new_obj = SurfaceMeasurements(**item)
                self.ScanwebSurfaceMeasurements.append(new_obj)

        measure_list = kwargs.get("ScanwebSubSurfaceMeasurements")
        if measure_list:
            for item in measure_list:
                new_obj = SubSurfaceMeasurements(**item)
                self.ScanwebSubSurfaceMeasurements.append(new_obj)


def _get_scanweb_response(accesscode=_DEFAULT_ACCESS_CODE):
    url = URLS["Scanweb"]
    stderr.write(url)
    stderr.write("\n")
    r = requests.get(url, params={"AccessCode": accesscode})
    return r

def get_scanweb_json(accesscode=_DEFAULT_ACCESS_CODE):
    response = _get_scanweb_response(accesscode)
    return response.content.decode('utf-8')

def get_scanweb(accesscode=_DEFAULT_ACCESS_CODE):
    response = _get_scanweb_response(accesscode)
    return response.json()

