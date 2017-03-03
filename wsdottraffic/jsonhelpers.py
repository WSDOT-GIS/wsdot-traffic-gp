"""Provides functions and custom encoder classes for serializing traveler info
objects to JSON.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import json
import re

from .parseutils import parse_wcf_date


def _simplfy_field_name(field_name):
    """Returns simplified versions of field names from the API are
    unnecessarily complex.
    """
    unneeded_prefix_re = re.compile(
        r"""^(
                (?:
                    (?:BorderCrossing)|(?:FlowStation)|(?:Camera)
                )Location
             )
        """,
        re.VERBOSE)
    description_re = re.compile(r"Description$")

    match = unneeded_prefix_re.match(field_name)
    if match:
        if description_re.search(field_name):
            replacement = "Location"
        else:
            replacement = ""
        return field_name.replace(match.group(), replacement)

    location_name_re = re.compile(r"""^(
        (?P<start>
            (?:Start)|
            (?:Begin)
        )|(?P<end>End)
    )\w*(?P<prop_desc>
        (RoadName)|
        (Longitude)|
        (Latitude)|
        (MilePost)|
        (Description)|
        (Direction)
    )$
    """, re.VERBOSE | re.IGNORECASE)

    match = location_name_re.match(field_name)

    if match:
        if match.group("start"):
            return match.expand(r"Start\g<prop_desc>")
        else:
            return match.expand(r"End\g<prop_desc>")

    return field_name


def parse_traveler_info_object(dct):
    """This method is used by the json.load method to customize how the
    traffic info objects are deserialized.
    @type dct: dict
    @return: dictionary with flattened JSON output
    @rtype: dict
    """
    output = {}
    for key, val in dct.items():
        if isinstance(val, dict):
            # Roadway locations will be "flattened", since tables can't have
            # nested values.
            for roadway_location_key in val:
                new_key = key + roadway_location_key
                new_key = _simplfy_field_name(new_key)
                if len(new_key) == 0 and val[roadway_location_key] is None:
                    continue
                output[new_key] = val[roadway_location_key]
        else:
            simplified_key = _simplfy_field_name(key)
            if len(simplified_key) == 0 and val is None:
                continue
            if simplified_key == "LocationID":
                output[simplified_key] = "{%s}" % val
            elif isinstance(val, str):
                # Parse date/time values.
                # Either parses into date (if possible) or returns the original
                # string.
                output[simplified_key] = parse_wcf_date(val.strip())
            else:
                output[simplified_key] = val
    return output


def _dict_has_all_keys(dct, *keys):
    for key in keys:
        if key not in dct:
            return False
    return True


def to_geo_json(dct):
    """This method is used by the json.load method to customize how
    the traffic info objects are deserialized.
    @type dct: dict
    @return: dictionary with GeoJSON output
    @rtype: dict
    """
    outdict = {
        "type": "Feature",
    }
    prop_dict = {}
    nonproperty_fields = ()
    point_geo_fields = ("Longitude", "Latitude")
    multi_point_geo_fields = (
        "StartLongitude", "StartLatitude", "EndLongitude", "EndLatitude"
    )
    if _dict_has_all_keys(dct, *point_geo_fields):
        outdict["geometry"] = {
            "type": "Point",
            "coordinates": [
                dct["Longitude"],
                dct["Latitude"]
            ]
        }
        nonproperty_fields = point_geo_fields
    elif _dict_has_all_keys(dct, *multi_point_geo_fields):
        outdict["geometry"] = {
            "type": "MultiPoint",
            "coordinates": [
                [dct["StartLongitude"], dct["StartLatitude"]],
                [dct["EndLongitude"], dct["EndLatitude"]]
            ]
        }
        nonproperty_fields = multi_point_geo_fields
    for key, value in dct.items():
        if key in nonproperty_fields:
            continue
        prop_dict[key] = value
    outdict["properties"] = prop_dict
    return outdict


def dict_list_to_geojson(dicts):
    """Converts a list of dicts, returned from parse_traveler_info_object
    into a GeoJSON FeatureCollection.
    """

    output = {
        "type": "FeatureCollection",
        "features": list(map(to_geo_json, dicts))
    }

    return output


class CustomEncoder(json.JSONEncoder):
    """Used for controlling formatting.
    Outputs dates as ISO format string.
    """

    def default(self, obj):  # pylint: disable=method-hidden
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        return super().default(obj)
