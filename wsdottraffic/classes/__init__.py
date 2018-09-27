"""Defines Python data classes for Traffic API
"""
# pylint: disable=invalid-name
import copy
import datetime
from dataclasses import dataclass, asdict
import enum
import uuid
import json
from typing import Sequence, Tuple, ClassVar
import dateutil.parser
from ..parseutils import parse_wcf_date
from ..dicttools import flatten_dict

CoorPair = Tuple[float, float]


def _get_coord_pairs(o: object, *coord_fields: str) -> CoorPair or Tuple[CoorPair]:
    # Get the number of provided field names.
    field_count = len(coord_fields)
    # Reduce count by one if there is an odd number of field names.
    if field_count % 2 != 0:
        field_count -= 1
    output = []
    i = 0  # initialize counter.
    while i < field_count:
        x, y = tuple(map(getattr, (o,)*2, coord_fields[i:i+2], (None,)*2))
        if not isinstance(x, float) or not isinstance(y, float):
            raise TypeError("Non-numeric value: %s." % ((x, y),))
        if x is not None and y is not None:
            output.append((x, y))
        i += 2
    if not output:
        return None
    return tuple(output)


def make_geo_interface(o: object, *coord_fields: str, id_field: str = None) -> dict:
    """Creates a __geo_interface__ dict using object properties.

    See https://gist.github.com/sgillies/2217756

    Args:
        o: The object that is being converted into a __geo_interface__ dict.
        coord_fields: the names of two or more fields that contain coordinate values.
            The names in even-numbered positions are X values, odd are Y.
        id_field: The name of the field that provides a unique str or int identifier.
            This becomes the dict's "id" value if provided.

    Returns:
        Returns a dict that implements __geo_interface__.
    """
    default_coord_fields = ("Longitude", "Latitude")
    if not coord_fields and ("Longitude" and "Latitude") in o.__annotations__:
        coord_fields = default_coord_fields
    if not coord_fields:
        raise TypeError("No coord_fields were provided")

    field_count = len(coord_fields)
    if field_count < 2:
        raise ValueError("coord_fields must have at least two values")

    # If there are an odd number of fields, remove the last one.
    if field_count % 2 != 0:
        coord_fields = coord_fields[0:-1]

    # Get the coordinates
    coords: Tuple[float, float] or Tuple[Tuple[float, float]]
    if len(coord_fields) <= 3:
        coords = tuple(map(getattr, (o,)*2, coord_fields[0:2], (None,)*2))
    else:
        coords = _get_coord_pairs(o, *coord_fields)

    # Create the dict for "properties" and remove the coordinate fields.
    props = dict(flatten_dict(o, json_safe=True))
    for prop_name in coord_fields:
        props.pop(prop_name, None)

    # Get the "id", removing from props if provided.
    _id: str or int = None
    if id_field is not None:
        _id = props.pop(id_field, None)

    if coords:
        geometry = {
            "coordinates": coords
        }
        if len(coord_fields) > 2:
            geometry["type"] = "MultiPoint"
        else:
            geometry["type"] = "Point"
    else:
        geometry = None

    output = {
        "type": "Feature",
        "properties": props,
        "geometry": geometry
    }

    if _id is not None:
        output["id"] = _id

    return output


def create_point_geo_interface(x: float, y: float) -> dict:
    """Provided an X and Y coordinate, returns a __geo_interface__ Point dict.
    """
    if x and y:
        coords = (x, y)
    else:
        coords = None
    if coords:
        return {
            "type": "Point",
            "coordinates": coords
        }
    return None


def get_multipoint_feature(dct: dict, *xy_props: Sequence[Sequence[str]]):
    """Converts a flattened dictionary into a multipoint feature
    geometry interface (__geo_interface__).

    Args:
        dct: dictionary of properties
        xy_props: tuple containging the names of the properties
            that define longitude and latitude, respectively.

    Returns:
        A dict defining a __geo_interface__
    """
    if len(xy_props) % 2 != 0:
        raise ValueError("xy_props must have even number of elements")
    props = dict(flatten_dict(dct))

    coords = []
    for x_key, y_key in xy_props:
        x, y = map(props.pop, (x_key, y_key), (None,)*2)
        if x is not None and y is not None:
            coords.append((x, y))
    coords = tuple(coords)
    geo = {
        "type": "MultiPoint",
        "coordinates": coords
    }
    return {
        "type": "Feature",
        "properties": props,
        "geometry": geo
    }


@enum.unique
class CommercialVehicleRestrictionType(enum.IntEnum):
    """Commercial Vehicle Type

    Values:
        BridgeRestriction: 0
        RoadRestriction: 1
    """
    BridgeRestriction = 0
    RoadRestriction = 1


@dataclass
class RoadwayLocation():
    """Describes a point along a WSDOT route.

    See https://www.wsdot.wa.gov/Traffic/api/Documentation/class_roadway_location.html

    Attributes:
        Description: A description of the location. This could be a cross street or a
            nearby landmark.
        Direction: The side of the road the location is on (Northbound, Southbound).
            This does not necessarily correspond to an actual compass direction.
        Latitude: Latitude of the location.
        Longitude: Longitude of the location.
        MilePost: The milepost of the location.
        RoadName: The name of the road.
    """
    Description: str = None
    RoadName: str = None
    Direction: str = None
    MilePost: float = None
    Latitude: float = None
    Longitude: float = None

    def __post_init__(self):
        for name in ("Longitude", "Latitude"):
            val = getattr(self, name, None)
            if val == 0:
                setattr(self, name, None)

    # @property
    # def as_geometry(self) -> dict:
    #     """Converts to __geo_interface__ Point.
    #     """
    #     return {
    #         "type": "Point",
    #         "coodrinates": (self.Longitude, self.Latitude)
    #     }

    # @property
    # def __geo_interface__(self):
    #     props = dict(flatten_dict(self))
    #     x = props.pop("Longitude", None)
    #     y = props.pop("Latitude", None)

    #     return {
    #         "type": "Feature",
    #         "properties": {
    #             "Description": props
    #         },
    #         "geometry": (x, y)
    #     }


@dataclass
class BorderCrossingData():
    """Describes a WA/Canada border crossing and wait time.

    See https://www.wsdot.wa.gov/Traffic/api/Documentation/class_border_crossing_data.html
    """
    Time: datetime.datetime = None
    CrossingName: str = None
    BorderCrossingLocation: RoadwayLocation = None
    WaitTime: int = None

    def __post_init__(self):
        if self.Time and isinstance(self.Time, str):
            self.Time = parse_wcf_date(self.Time)
        if (self.BorderCrossingLocation and not
                isinstance(self.BorderCrossingLocation, RoadwayLocation)):
            self.BorderCrossingLocation = RoadwayLocation(
                **self.BorderCrossingLocation)  # pylint:disable=not-a-mapping

    @property
    def __geo_interface__(self):
        props = dict(flatten_dict(self))
        x, y = map(props.pop, (
            "BorderCrossingLocationLongitude",
            "BorderCrossingLocationLatitude"), (None,)*2)
        geo = create_point_geo_interface(x, y)
        return {
            "type": "Feature",
            "properties": props,
            "geometry": geo
        }


@dataclass
class BridgeDataGIS():
    """Bridge Data

    See https://www.wsdot.wa.gov/Traffic/api/Documentation/class_bridge_data_g_i_s.html
    """
    LocationID: uuid.UUID
    StructureID: str = None
    StateRouteID: str = None
    IsConnector: bool = None
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
        if self.IsConnector is not None and not isinstance(self.IsConnector, bool):
            self.IsConnector = bool(self.IsConnector)
        if self.LocationID and not isinstance(self.LocationID, uuid.UUID):
            self.LocationID = uuid.UUID(self.LocationID)

    @property
    def __geo_interface__(self):
        props = dict(flatten_dict(self))

        # Convert UUID to serializeable string
        props["LocationID"] = str(self.LocationID)

        x1, y1, x2, y2 = map(
            props.pop, ("BeginLongitude", "BeginLatitude", "EndLongitude", "EndLatitude"))

        geom = {}
        geom["type"] = "MultiPoint"
        if (x1 and y1 and x2 and y2):
            geom["coordinates"] = ((x1, y1), (x2, y2))
        elif (x1 and y1):
            geom["coordinates"] = ((x1, y1))
        elif (x2 and y2):
            geom["coordinates"] = ((x2, y2))

        return {
            "type": "Feature",
            "properties": props,
            "geometry": geom
        }


@dataclass
class CVRestrictionData():
    """Commercial Vehicle Restriction data.

    See https://www.wsdot.wa.gov/Traffic/api/Documentation/class_c_v_restriction_data.html
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
    MaximumGrossVehicleWeightInPounds: int = None  # pylint: disable=invalid-name
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
            self.RestrictionType = CommercialVehicleRestrictionType(  # pylint: disable=invalid-name
                self.RestrictionType)
        for name in ("StartRoadwayLocation", "EndRoadwayLocation"):
            val = getattr(self, name, None)
            if val is not None and not isinstance(val, RoadwayLocation):
                # pylint: disable=not-a-mapping
                setattr(self, name, RoadwayLocation(**val))
        for name in ("DatePosted", "DateEffective", "DateExpires"):
            val = getattr(self, name, None)
            if isinstance(val, str):
                setattr(self, name, parse_wcf_date(val))

    @property
    def __geo_interface__(self):
        props = dict(flatten_dict(self))
        x, y = map(props.pop, ("Longitude", "Latitude"), (None,)*2)
        geom = {
            "type": "Point",
            "coordinates": (x, y)
        }
        return {
            "type": "Feature",
            "geometry": geom,
            "properties": props
        }


@dataclass
class Alert():
    """Highway Alert

    See https://www.wsdot.wa.gov/Traffic/api/Documentation/class_alert.html
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

    @property
    def __geo_interface__(self):
        return get_multipoint_feature(asdict(self), (
            "StartRoadwayLocationLongitude", "StartRoadwayLocationLatitude"
        ), (
            "EndRoadwayLocationLongitude", "EndRoadwayLocationLatitude"
        ))


@dataclass
class Camera():
    """Highway Camera

    See https://www.wsdot.wa.gov/Traffic/api/Documentation/class_camera.html

    Attributes:
        CameraID: Unique identifier for the camera
        CameraLocation: Structure identifying where the camera is located
        CameraOwner: Owner of camera when not WSDOT
        Description: Short description for the camera
        DisplayLatitude: Latitude of where to display the camera on a map
        DisplayLongitude: Longitude of where to display the camera on a map
        ImageHeight: Pixel height of the image
        ImageURL: Stored location of the camera image
        ImageWidth: Pixel width of the image
        IsActive: Indicator if the camera is still actively being updated
        OwnerURL: Website for camera owner when not WSDOT
        Region: WSDOT region which owns the camera
        SortOrder: When more than one camera is located in the same area this is order of display
        Title: Title for the camera
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
            self.CameraLocation = RoadwayLocation(
                **self.CameraLocation)  # pylint:disable=not-a-mapping

    @property
    def __geo_interface__(self):
        props = dict(flatten_dict(self))

        dx, dy, x, y = map(props.pop, (
            "DisplayLongitude",
            "DisplayLatitude",
            "CameraLocationLongitude",
            "CameraLocationLatitude",
        ), (None,)*4)

        if not x and dx:
            x = dx
        if not y and dy:
            y = dy

        return {
            "type": "Feature",
            "properties": props,
            "geometry": create_point_geo_interface(x, y)
        }


@dataclass
class TravelRestriction():
    """Describes a travel restriction

    See https://www.wsdot.wa.gov/Traffic/api/Documentation/class_travel_restriction.html
    """
    TravelDirection: str = None

    RestrictionText: str = None


@dataclass
class PassCondition():
    """Mountain pass condition

    See https://www.wsdot.wa.gov/Traffic/api/Documentation/class_pass_condition.html
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
            self.RestrictionOne = TravelRestriction(
                **self.RestrictionOne)  # pylint:disable=not-a-mapping
        if not isinstance(self.RestrictionTwo, TravelRestriction):
            self.RestrictionTwo = TravelRestriction(
                **self.RestrictionTwo)  # pylint:disable=not-a-mapping

    @property
    def __geo_interface__(self):
        props = dict(flatten_dict(self))

        x = props.pop("Longitude", None)
        y = props.pop("Latitude", None)
        geometry: dict = None
        if (x and y):
            geometry = create_point_geo_interface(x, y)
        output = {
            "type": "Feature",
            "properties": props,
            "geometry": geometry
        }
        return output


@enum.unique
class FlowStationReading(enum.IntEnum):
    """Flow station reading

    Values:
        Unknown: 0
        WideOpen: 1
        Moderate: 2
        Heavy: 3
        StopAndGo: 4
        NoData: 5
    """
    Unknown = 0
    WideOpen = 1
    Moderate = 2
    Heavy = 3
    StopAndGo = 4
    NoData = 5


@dataclass
class FlowData():
    """Flow data

    See: https://www.wsdot.wa.gov/Traffic/api/Documentation/class_flow_data.html
    """
    FlowDataID: int = None

    Time: datetime.datetime = None

    StationName: str = None

    Region: str = None

    FlowStationLocation: RoadwayLocation = None

    FlowReadingValue: FlowStationReading = FlowStationReading.Unknown

    def __post_init__(self):
        if isinstance(self.Time, str):
            self.Time = parse_wcf_date(self.Time)
        if not isinstance(self.FlowStationLocation, RoadwayLocation):
            self.FlowStationLocation = RoadwayLocation(
                **self.FlowStationLocation)  # pylint: disable=not-a-mapping
        if not isinstance(self.FlowReadingValue, FlowStationReading):
            self.FlowReadingValue = FlowStationReading(self.FlowReadingValue)

    @property
    def __geo_interface__(self):
        props = dict(flatten_dict(self))
        x, y = map(lambda name: props.pop(name, None),
                   ("FlowStationLocationLongitude", "FlowStationLocationLatitude"))
        geom = create_point_geo_interface(x, y)
        flow_data_id = props.pop("FlowDataID")
        return {
            "type": "Feature",
            "id": flow_data_id,
            "properties": props,
            "geometry": geom
        }


@dataclass
class TravelTimeRoute():
    """Travel time route

    See https://www.wsdot.wa.gov/Traffic/api/Documentation/class_travel_time_route.html
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
            if isinstance(val, dict):
                # pylint: disable=not-a-mapping
                setattr(self, name, RoadwayLocation(**val))

    @property
    def __geo_interface__(self):
        return get_multipoint_feature(
            self, ("StartPointLongitude", "EndPointLongitude"),
            ("StartPointLatitude", "EndPointLatitude"))


@dataclass
class WeatherStation():
    """Weather Station
    """
    StationCode: int
    StationName: str
    Longitude: float
    Latitude: float

    @property
    def __geo_interface__(self):
        return make_geo_interface(self, id_field="StationCode")


@dataclass
class WeatherInfo():
    """Weather info

    See https://www.wsdot.wa.gov/Traffic/api/Documentation/class_weather_info.html
    """
    StationID: int

    StationName: str

    Latitude: float

    Longitude: float

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

    @property
    def __geo_interface__(self):
        return make_geo_interface(self, id_field="StationID")


@dataclass
class TollRate():
    # pylint:disable=line-too-long
    """Toll rate

    See https://www.wsdot.wa.gov/Traffic/api/Documentation/class_traveler_a_p_i_1_1_models_1_1_toll_rate.html

    Attention: The tolls reported here may not match what is currently displayed on
    the road signs due to timing issues between WSDOT and the tolling contractor.

    Attributes:
        CurrentMessage: Message displayed on the sign in place of a toll
        CurrentToll: The computed toll in cents which is sent to the tolling company,
            may not match what is displayed on the sign due to timing issues
        EndLatitude: Approximate geographical latitude of the end location
        EndLocationName: Common name of the end location
        EndLongitude: Approximate geographical longitude of the end location
        EndMilepost: The end milepost for a toll trip
        SignName: Name of sign
        StartLatitude: Approximate geographical latitude of the start location
        StartLocationName: Common name of the start location
        StartLongitude: Approximate geographical longitude of the start location
        StartMilepost: The start milepost for a toll trip
        StateRoute: Route the toll applies to
        TravelDirection: Travel direction the toll applies to
        TripName: Name for the toll trip
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

    @property
    def __geo_interface__(self):
        props = dict(flatten_dict(self))
        x1, y1, x2, y2 = map(props.pop, (
            "StartLongitude", "StartLatitude", "EndLongitude", "EndLatitude"), (None,)*4)
        geom = {
            "type": "MultiPoint",
            "coordinates": ((x1, y1), (x2, y2))
        }
        return {
            "type": "Feature",
            "properties": props,
            "geometry": geom
        }


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
            new_list = getattr(self, attrib_name, None)
            if new_list is None:
                continue

            if attrib_name == "SurfaceMeasurements":
                ctor = SurfaceMeasurements
            else:
                ctor = SubSurfaceMeasurements

            new_list = tuple(map(lambda item: ctor(**item), new_list))
            setattr(self, attrib_name, new_list)

    def __geo_interface__(self):
        # Create feature properties dict.
        props = asdict(self)
        # Remove the X and Y coordinates from properties
        x = props.pop("Longitude")
        y = props.pop("Latitude")
        # Create geometry from x and y
        geometry = create_point_geo_interface(x, y)
        # get feature ID
        _id = props.pop("StationId")

        # TODO: Convert SurfaceMeasurements and SubSurfaceMeasurements
        # to value compatible with GeoJSON property.
        for attrib_name in ("SurfaceMeasurements", "SubSurfaceMeasurements"):
            val = props.pop(attrib_name, None)
            if not val:
                continue
            val = map(asdict, val)
            val = json.dumps(val)
            props[attrib_name] = val

        return {
            "id": _id,
            "type": "Feature",
            "properties": props,
            "geometry": geometry
        }


def parse(dct: dict):
    """Specialized JSON parsing for wsdottraffic.classes classes.
    For use with the json.load and json.loads object_hook parameter.
    """
    # pylint: disable=too-many-return-statements
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
    if "MountainPassId" in dct:
        return PassCondition(**dct)
    if "FlowDataID" in dct:
        return FlowData(**dct)
    if "TravelTimeID" in dct:
        return TravelTimeRoute(**dct)
    if "StationID" in dct:
        return WeatherInfo(**dct)
    if "StationCode" in dct:
        return WeatherStation(**dct)
    if "CurrentToll" in dct:
        return TollRate(**dct)
    if "StationId" in dct:
        return WeatherReading(**dct)
    return dct


class TrafficJSONEncoder(json.JSONEncoder):
    """Encodes wsdottraffic classes back to JSON.
    Date objects are represented in ISO format strings rather than WCF date strings.
    """

    def default(self, o):  # pylint:disable=method-hidden
        """Converts the input object into a JSON serializable object.
        """
        if isinstance(o, enum.Enum):
            return o.name
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        if isinstance(o, uuid.UUID):
            return str(o)
        if not isinstance(o, (
                BorderCrossingData,
                BridgeDataGIS,
                CVRestrictionData,
                Alert,
                Camera,
                TravelRestriction,
                WeatherStation,
                WeatherReading,
                SurfaceMeasurements,
                SubSurfaceMeasurements,
                PassCondition,
                FlowData,
                TravelTimeRoute,
                WeatherInfo,
                TollRate,
                RoadwayLocation)):
            return super().default(o)
        return o.__dict__
