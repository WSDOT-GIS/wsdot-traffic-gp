"""This module is for the Scanweb REST endpoint
"""

from __future__ import unicode_literals, print_function, absolute_import, division
import json
import datetime
from typing import Sequence
from dataclasses import dataclass
from sys import stderr

import dateutil.parser
import requests
from ..resturls import URLS
from .. import _DEFAULT_ACCESS_CODE

# pylint: disable=invalid-name,too-few-public-methods

@dataclass
class SurfaceMeasurements():
    """Surface Measurement

    Attributes:
        SensorId: byte
        SurfaceTemperature: decimal
        RoadFreezingTemperature: decimal
        RoadSurfaceCondition: int
    """
    SensorId: int
    SurfaceTemperature: float
    RoadFreezingTemperature: float
    RoadSurfaceCondition: int

@dataclass
class SubSurfaceMeasurements():
    """Sub-Surface Measurement

    Attributes:
        SensorId: byte
        SubSurfaceTemperature: decimal
    """
    SensorId: int
    SubSurfaceTemperature: float


@dataclass
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

    StationId: str = None
    StationName: str = None
    Latitude: float = None
    Longitude: float = None
    Elevation: int = None
    ReadingTime: datetime.datetime = None
    AirTemperature: float = None
    RelativeHumidty: int = None
    AverageWindSpeed: int = None
    AverageWindDirection: int = None
    WindGust: int = None
    Visibility: int = None
    PrecipitationIntensity: int = None
    PrecipitationType: int = None
    PrecipitationPast1Hour: float = None
    PrecipitationPast3Hours: float = None
    PrecipitationPast6Hours: float = None
    PrecipitationPast12Hours: float = None
    PrecipitationPast24Hours: float = None
    PrecipitationAccumulation: float = None
    BarometricPressure: int = None
    SnowDepth: int = None
    SurfaceMeasurements: Sequence[SurfaceMeasurements] = None
    SubSurfaceMeasurements: Sequence[SubSurfaceMeasurements] = None

    def __post_init__(self):
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
        if isinstance(self.ReadingTime, str):
            self.ReadingTime = dateutil.parser.parse(self.ReadingTime)

        ctor: SurfaceMeasurements or SubSurfaceMeasurements = None
        for attrib_name in ("SurfaceMeasurements", "SubSurfaceMeasurements"):
            new_list = getattr(attrib_name, None)
            if new_list is None:
                continue

            if attrib_name == "SurfaceMeasurements":
                ctor = SurfaceMeasurements
            else:
                ctor = SubSurfaceMeasurements

            new_list = map(lambda item: ctor(**item))
            setattr(attrib_name, new_list)

class ScanwebJsonEncoder(json.JSONEncoder):
    """Custom JSONEncoder class for use with the cls argument of json.dump and json.dumps.
    """
    def default(self, o): # pylint: disable=method-hidden
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if isinstance(o, (WeatherReading, SurfaceMeasurements, SubSurfaceMeasurements)):
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
