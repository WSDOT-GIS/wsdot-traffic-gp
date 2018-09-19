"""This module is for the Scanweb REST endpoint
"""

from __future__ import unicode_literals, print_function, absolute_import, division
import json
import datetime
from sys import stderr
import dateutil.parser
import requests
from ..resturls import URLS
from .. import _DEFAULT_ACCESS_CODE

# pylint: disable=invalid-name,too-few-public-methods

class SurfaceMeasurements():
    """Surface Measurement

    Attributes:
        SensorId: byte
        SurfaceTemperature: decimal
        RoadFreezingTemperature: decimal
        RoadSurfaceCondition: int
    """
    def __init__(self, **kwargs):
        self.SensorId = kwargs.get("SensorId")
        self.SurfaceTemperature = kwargs.get("SurfaceTemperature")
        self.RoadFreezingTemperature = kwargs.get("RoadFreezingTemperature")
        self.RoadSurfaceCondition = kwargs.get("RoadSurfaceCondition")


class SubSurfaceMeasurements():
    """Sub-Surface Measurement

    Attributes:
        SensorId: byte
        SubSurfaceTemperature: decimal
    """
    def __init__(self, **kwargs):
        self.SensorId = kwargs.get("SensorId")
        self.SubSurfaceTemperature = kwargs.get("SubSurfaceTemperature")


class WeatherReading():
    """Scanweb Weather Reading

    Attributes:
        StationId: string
        StationName: string
        Latitude: decimal
        Longitude: decimal
        Elevation: int
        ReadingTime: DateTime
        AirTemperature: decimal
        RelativeHumidty: byte
        AverageWindSpeed: byte
        AverageWindDirection: short
        WindGust: byte
        Visibility: short
        PrecipitationIntensity: byte
        PrecipitationType: byte
        PrecipitationPast1Hour: decimal
        PrecipitationPast3Hours: decimal
        PrecipitationPast6Hours: decimal
        PrecipitationPast12Hours: decimal
        PrecipitationPast24Hours: decimal
        PrecipitationAccumulation: decimal
        BarometricPressure: int
        SnowDepth: int
        SurfaceMeasurements: Sequence[ScanwebSurfaceMeasurements]
        SubSurfaceMeasurements: Sequence[ScanwebSubSurfaceMeasurements]
    """

    def __init__(self, **kwargs):
        """Scanweb Weather Reading

        Args:
            StationId: string
            StationName: string
            Latitude: decimal
            Longitude: decimal
            Elevation: int
            ReadingTime: DateTime
            AirTemperature: decimal
            RelativeHumidty: byte
            AverageWindSpeed: byte
            AverageWindDirection: short
            WindGust: byte
            Visibility: short
            PrecipitationIntensity: byte
            PrecipitationType: byte
            PrecipitationPast1Hour: decimal
            PrecipitationPast3Hours: decimal
            PrecipitationPast6Hours: decimal
            PrecipitationPast12Hours: decimal
            PrecipitationPast24Hours: decimal
            PrecipitationAccumulation: decimal
            BarometricPressure: int
            SnowDepth: int
            SurfaceMeasurements: Sequence[ScanwebSurfaceMeasurements]
            SubSurfaceMeasurements: Sequence[ScanwebSubSurfaceMeasurements]
        """
        self.StationId = kwargs.get("StationId")
        self.StationName = kwargs.get("StationName")
        self.Latitude = kwargs.get("Latitude")
        self.Longitude = kwargs.get("Longitude")
        self.Elevation = kwargs.get("Elevation")
        self.ReadingTime = None
        if "ReadingTime" in kwargs:
            date_str = kwargs.get("ReadingTime")
            if date_str:
                self.ReadingTime = dateutil.parser.parse(date_str)
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

        measure_list = kwargs.get("SurfaceMeasurements")
        new_list = []
        if measure_list:
            for item in measure_list:
                new_obj = SurfaceMeasurements(**item)
                new_list.append(new_obj)
        self.SurfaceMeasurements = new_list

        measure_list = kwargs.get("SubSurfaceMeasurements")
        new_list = []
        if measure_list:
            for item in measure_list:
                new_obj = SubSurfaceMeasurements(**item)
                new_list.append(new_obj)
        self.SubSurfaceMeasurements = new_list

class ScanwebJsonEncoder(json.JSONEncoder):
    """Custom JSONEncoder class for use with the cls argument of json.dump and json.dumps.
    """
    def default(self, o): # pylint: disable=method-hidden
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, (WeatherReading, SurfaceMeasurements, SubSurfaceMeasurements)):
            return o.__dict__
        return json.JSONEncoder.default(self, o)


def scanweb_json_hook(dct):
    """For use with the object_hook parameter of json.load and json.loads.
    Parses json into specialized objects.
    """
    if "StationId" in dct:
        return WeatherReading(**dct)
    return dct

def _get_scanweb_response(accesscode=_DEFAULT_ACCESS_CODE):
    url = URLS["Scanweb"]
    stderr.write(url)
    stderr.write("\n")
    r = requests.get(url, params={"AccessCode": accesscode})
    return r

def get_scanweb_json(accesscode=_DEFAULT_ACCESS_CODE):
    """Gets the scanweb response as a JSON string.
    """
    response = _get_scanweb_response(accesscode)
    return response.content.decode('utf-8')

def get_scanweb(accesscode=_DEFAULT_ACCESS_CODE):
    """Gets the scanweb response as JSON objects.
    """
    response = _get_scanweb_response(accesscode)
    return response.json(object_hook=scanweb_json_hook)
