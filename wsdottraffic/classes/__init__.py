"""Defines Python data classes for Traffic API
"""
import datetime
from dataclasses import dataclass
import enum
import uuid
import json
from ..parseutils import parse_wcf_date

@enum.unique
class CommercialVehicleRestrictionType(enum.IntEnum):
    """Commercial Vehicle Type
    """
    BridgeRestriction = 0
    RoadRestriction = 1

@dataclass
class RoadwayLocation(object):
    """Describes a point along a WSDOT route.
    """
    Description: str = None
    RoadName: str = None
    Direction: str = None
    MilePost: float = None
    Latitude: float = None
    Longitude: float = None


@dataclass
class BorderCrossingData(object):
    """Describes a WA/Canada border crossing and wait time.
    """
    Time: datetime.datetime = None
    CrossingName: str = None
    BorderCrossingLocation: RoadwayLocation = None
    WaitTime: int = None

    def __post_init__(self):
        if self.Time and isinstance(self.Time, str):
            self.Time = parse_wcf_date(self.Time)
        if self.BorderCrossingLocation and not isinstance(self.BorderCrossingLocation, RoadwayLocation):
            self.BorderCrossingLocation = RoadwayLocation(**self.BorderCrossingLocation)

@dataclass
class BridgeDataGIS(object):
    """Bridge Data
    """
    LocationID: uuid.UUID
    StructureID: str = None
    StateRouteID: str = None
    IsConnector: int = None
    BeginLatitude: float = None
    BeginLongitude: float = None
    BeginMilePost: float = None
    EndLatitude: float = None
    EndLongitude: float = None
    EndMilePost: float = None
    MaximumVerticalClearance: str = None
    MaximumVerticalClearanceInches: int = None
    MinimumVerticalClearance: str = None
    MinimumVerticalClearanceInches: int = None
    LRSRoute: str = None
    BridgeName: str = None

    def __post_init__(self):
        if self.LocationID and not isinstance(self.LocationID, uuid.UUID):
            self.LocationID = uuid.UUID(self.LocationID)

@dataclass
class CVRestrictionData(object):
    """Commercial Vehicle Restriction data.
    """
    StateRouteID: str = None
    State: str = None
    RestrictionWidthInInches: int = None
    RestrictionHeightInInches: int = None
    RestrictionLengthInInches: int = None
    RestrictionWeightInPounds: int = None
    IsDetourAvailable: bool = None
    IsPermanentRestriction: bool = None
    IsExceptionsAllowed: bool = None
    IsWarning: bool = None
    DatePosted: datetime.datetime = None
    DateEffective: datetime.datetime = None
    DateExpires: datetime.datetime = None
    LocationName: str = None
    LocationDescription: str = None
    RestrictionComment: str = None
    Latitude: float = None
    Longitude: float = None
    BridgeNumber: str = None
    MaximumGrossVehicleWeightInPounds: int = None
    BridgeName: str = None
    BLMaxAxle: int = None
    CL8MaxAxle: int = None
    SAMaxAxle: int = None
    TDMaxAxle: int = None
    VehicleType: str = None
    RestrictionType: CommercialVehicleRestrictionType = None
    StartRoadwayLocation: RoadwayLocation = None
    EndRoadwayLocation: RoadwayLocation = None

    def __post_init__(self):
        if not isinstance(self.RestrictionType, CommercialVehicleRestrictionType):
            self.RestrictionType = CommercialVehicleRestrictionType(self.RestrictionType)
        for name in ("DatePosted", "DateEffective", "DateExpires"):
            val = getattr(self, name, None)
            if isinstance(val, str):
                setattr(self, name, parse_wcf_date(val))

@dataclass
class Alert(object):
    """Highway Alert
    """
    AlertID: int = None

    StartRoadwayLocation: RoadwayLocation = None

    EndRoadwayLocation: RoadwayLocation = None

    Region: str = None

    County: str = None

    StartTime: datetime.datetime = None

    EndTime: datetime.datetime = None

    EventCategory: str = None

    HeadlineDescription: str = None

    ExtendedDescription: str = None

    EventStatus: str = None

    LastUpdatedTime: datetime.datetime = None

    Priority: str = None

    def __post_init__(self):
        if isinstance(self.StartTime, str):
            self.StartTime = parse_wcf_date(self.StartTime)
        if isinstance(self.EndTime, str):
            self.EndTime = parse_wcf_date(self.EndTime)
        if isinstance(self.LastUpdatedTime, str):
            self.LastUpdatedTime = parse_wcf_date(self.LastUpdatedTime)


@dataclass
class Camera(object):
    """Highway Camera
    """
    CameraID: int = None

    Region: str = None

    CameraLocation: RoadwayLocation = None

    DisplayLatitude: float = None

    DisplayLongitude: float = None

    Title: str = None

    Description: str = None

    ImageURL: str = None

    CameraOwner: str = None

    OwnerURL: str = None

    ImageWidth: int = None

    ImageHeight: int = None

    IsActive: bool = None

    SortOrder: int = None

    def __post_init__(self):
        if self.CameraLocation is not None and not isinstance(self.CameraLocation, RoadwayLocation):
            self.CameraLocation = RoadwayLocation(**self.CameraLocation)

@dataclass
class TravelRestriction(object):
    """Describes a travel restriction
    """
    TravelDirection: str = None

    RestrictionText: str = None

@dataclass
class PassCondition(object):
    """Mountain pass condition
    """
    MountainPassId: int = None

    MountainPassName: str = None

    Latitude: float = None

    Longitude: float = None

    DateUpdated: datetime.datetime = None

    TemperatureInFahrenheit: int = None

    ElevationInFeet: int = None

    WeatherCondition: str = None

    RoadCondition: str = None

    TravelAdvisoryActive: bool = None

    RestrictionOne: TravelRestriction = None

    RestrictionTwo: TravelRestriction = None

    def __post_init__(self):
        if isinstance(self.DateUpdated, str):
            self.DateUpdated = parse_wcf_date(self.DateUpdated)
        if not isinstance(self.RestrictionOne, TravelRestriction):
            self.RestrictionOne = TravelRestriction(**self.RestrictionOne)
        if not isinstance(self.RestrictionTwo, TravelRestriction):
            self.RestrictionTwo = TravelRestriction(**self.RestrictionTwo)


@enum.unique
class FlowStationReading(enum.IntEnum):
    """Flow station reading
    """
    Unknown = 0
    WideOpen = 1
    Moderate = 2
    Heavy = 3
    StopAndGo = 4
    NoData = 5

@dataclass
class FlowData(object):
    """Flow data
    """
    FlowDataID: int = None

    Time: datetime.datetime = None

    StationName: str = None

    Region: str = None

    FlowStationLocation: RoadwayLocation = None

    FlowReadingValue: FlowStationReading = None

    def __post_init__(self):
        if isinstance(self.Time, str):
            self.Time = parse_wcf_date(self.Time)
        if not isinstance(self.FlowStationLocation, RoadwayLocation):
            self.FlowStationLocation = RoadwayLocation(self.FlowStationLocation)
        if not isinstance(self.FlowReadingValue, FlowStationReading):
            self.FlowReadingValue = FlowStationReading(self.FlowReadingValue)

@dataclass
class TravelTimeRoute(object):
    """Travel time route
    """
    TravelTimeID: int = None
    Name: str = None
    Description: str = None
    TimeUpdated: datetime.datetime = None
    StartPoint: RoadwayLocation = None
    EndPoint: RoadwayLocation = None
    Distance: float = None
    AverageTime: int = None
    CurrentTime: int = None

    def __post_init__(self):
        if isinstance(self.TimeUpdated, str):
            self.TimeUpdated = parse_wcf_date(self.TimeUpdated)
        for name in ["StartPoint", "EndPoint"]:
            val = getattr(self, name, None)
            if isinstance(val, str):
                setattr(self, name, parse_wcf_date(val))

@dataclass
class WeatherInfo(object):
    """Weather info
    """
    StationID: int = None

    StationName: str = None

    Latitude: float = None

    Longitude: float = None

    ReadingTime: datetime.datetime = None

    TemperatureInFahrenheit: float = None

    PrecipitationInInches: float = None

    WindSpeedInMPH: float = None

    WindGustSpeedInMPH: float = None

    Visibility: int = None

    SkyCoverage: str = None

    BarometricPressure: float = None

    RelativeHumidity: float = None

    WindDirectionCardinal: str = None

    WindDirection: float = None

    def __post_init__(self):
        if isinstance(self.ReadingTime, str):
            self.ReadingTime = parse_wcf_date(self.ReadingTime)

@dataclass
class TollRate(object):
    """Toll rate
    """
    SignName: str = None

    TripName: str = None

    CurrentToll: int = None

    CurrentMessage: str = None

    StateRoute: str = None

    TravelDirection: str = None

    StartMilepost: float = None

    StartLocationName: str = None

    StartLatitude: float = None

    StartLongitude: float = None

    EndMilepost: float = None

    EndLocationName: str = None

    EndLatitude: float = None

    EndLongitude: float = None

def parse(dct: dict):
    """Specialized JSON parsing for wsdottraffic.classes classes.
    for use with the json.load and json.loads object_hook parameter.
    """
    if "BorderCrossingLocation" in dct:
        return BorderCrossingData(**dct)
    if "StructureID" in dct:
        return BridgeDataGIS(**dct)
    if "RestrictionType" in dct:
        return CVRestrictionData(**dct)
    if "AlertID" in dct:
        return Alert(**dct)
    if "CameraID" in dct:
        return Camera(**dct)
    if "MountainPassID" in dct:
        return PassCondition(**dct)
    if "FlowDataID" in dct:
        return FlowData(**dct)
    if "TravelTimeID" in dct:
        return TravelTimeRoute(**dct)
    if "StationID" in dct:
        return WeatherInfo(**dct)
    if "CurrentToll" in dct:
        return TollRate(**dct)
    return dct

class TrafficJSONEncoder(json.JSONEncoder):
    """Encodes wsdottraffic classes back to JSON.
    Date objects are represented in ISO format strings rather than WCF date strings.
    """
    def default(self, obj):
        """Converts the input object into a JSON serializable object.
        """
        if isinstance(obj, enum.Enum):
            return obj.name
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if not isinstance(obj, (BorderCrossingData, BridgeDataGIS, CVRestrictionData, Alert, Camera, PassCondition, FlowData, TravelTimeRoute, WeatherInfo, TollRate, RoadwayLocation)):
            return super().default(obj)
        return obj.__dict__
