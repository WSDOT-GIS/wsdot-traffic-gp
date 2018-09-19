'''Utilities for parsing strings into other types.
'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import time
import re
from typing import Tuple

WCF_DATE_RE = re.compile(
    r"\/Date\((?P<ms_since_1970_1_1>\d+)(?P<utc_offset>(?P<offset_sign>[+\-])(?P<offset_hrs>\d{2})(?P<offset_min>\d{2}))\)\/", re.IGNORECASE)
_CAMEL_CASE_RE = re.compile(r"(?:[A-Z][a-z]+)")

# ==RRTs (Related Roadway Type)==
# AR Alternate Route
# CD Collector Distributor (Dec)
# CI Collector Distributor (Inc)
# CO Couplet
# FI Frontage Road (Inc)
# FD Frontage Road (Dec)
# LX Crossroad within Interchange
# RL Reversible Lane
# SP Spur
# TB Transitional Turnback
# TR Temporary Route
# PR Proposed Route
# ===Ramps===
# P1 - P9 Off Ramp (Inc)
# PU Extension of P ramp
# Q1 - Q9 On Ramp (Inc)
# QU Extension of Q ramp
# R1 - R9 Off Ramp (Dec)
# RU Extension of R ramp
# S1 - S9 On Ramp (Dec)
# SU Extension of S ramp
# ==Ferries==
# FS Ferry Ship (Boat)
# FT Ferry Terminal

_ROUTE_ID_RE = re.compile(r"""^(?P<sr>\d{3})
    (?:
        (?P<rrt>
            (?:AR)|(?:C[DI])|(?:C[O])|(?:F[DI])|(?:LX)|(?:[PQRS][\dU])|(?:RL)|
            (?:SP)|(?:TB)|(?:TR)|(?:PR)|(?:F[ST])|(?:ML)
        )(?P<rrq>[A-Z0-9]{0,6})
    )?$""", re.VERBOSE)


class SRFormatError(ValueError):
    """Error for an invalid state route ID.
    """

    def __init__(self, value):
        """Creates a new instance
        """
        self.value = value
        super(SRFormatError, self).__init__()

    def __str__(self):
        """Converts object to string message.
        """
        msg_fmt = "Invalid route ID: %s"
        return msg_fmt % self.value


def parse_wcf_date(wcf_date: str, throw_on_wrong_format: bool = False, output_utc: bool = True) -> datetime.datetime or str:
    """Parses a WCF serialized date to a date string.

    See https://docs.microsoft.com/en-us/dotnet/framework/wcf/feature-details/stand-alone-json-serialization#datetime-wire-format

    Args:
        wcf_date: str. A date/time in WCF JSON serialized format.
        throw_on_wrong_format: Set to True to throw error on wrong format, False (default) to simply return original string.
        output_utc: Set to True (default) to output UTC time, false to include timezone info.
            This value will be ignored if the input wcf_date string does not include timezone info.
            See https://docs.python.org/3/library/datetime.html#timezone-objects

    Raises:
        TypeError: raised if wcf_date is not a string.
        ValueError: raised if wcf_date could not be parsed and thow_on_wrong_format is set to True.

    Returns:
        datetime.datetime or str
    """
    if not isinstance(wcf_date, str):
        raise TypeError("Only str and unicode types are supported.")
    match = WCF_DATE_RE.match(wcf_date)
    if match:
        groups = match.groups()

        ticks = None
        if not output_utc and len(groups) >= 2:
            # Use timezone info. See https://docs.python.org/3/library/datetime.html#timezone-objects
            groupdict = match.groupdict()
            ticks = int(groupdict["ms_since_1970_1_1"]) / 1000
            hrs = int(groupdict["offset_hrs"])
            mins = int(groupdict["offset_min"])
            if groupdict["offset_sign"] == "-":
                sign = -1
            else:
                sign = 1
            delta = datetime.timedelta(hours=hrs * sign, minutes=mins * sign)
            time_zone = datetime.timezone(delta)
            return datetime.datetime.fromtimestamp(ticks, time_zone)
        else:
            # Discard timezone info and use UTC time.
            ticks = int(groups[0]) / 1000
            return datetime.datetime.utcfromtimestamp(ticks)

    elif throw_on_wrong_format:
        raise ValueError("Could not parse as a WCF date string: %s." %
                         wcf_date)
    else:
        return wcf_date


def to_wcf_date(date_obj: datetime.datetime or datetime.date or datetime.time) -> str:
    """Converts a datetime.datetime object into a WCF date format string.

    Args:
        date_obj: A Python date and/or time object.

    Returns:
        Returns a WCF string representation of the input date/time.

    Raises:
        TypeError: Raised if input is not one of the expected Python date/time types.
    """
    if not isinstance(date_obj, (datetime.datetime, datetime.date,
                                 datetime.time)):
        raise TypeError("Must be datetime, date, or time")
    ticks = int(time.mktime(date_obj.timetuple()) * 1000)
    return "/Date(%d)/" % ticks


def split_camel_case(the_string: str) -> str:
    """Splits a camel case word into individual words separated by spaces

    Args:
        the_string: A camel-case word.

    Returns:
        A string with the words separated by spaces.
        Returns None if the_string was None.
    """
    if the_string is not None:
        words = _CAMEL_CASE_RE.findall(the_string)
        return " ".join(words)
    return None


def parse_route_id(route_id: str or int) -> Tuple[str, str or None, str or None]:
    """Parses a route identifier into its component parts: SR, RRT, RRQ

    For more details, see the Highway Log PDF files at
    http://www.wsdot.wa.gov/mapsdata/roadway/statehighwaylog.htm.

    Args:
        route_id: WSDOT route identifier (str) or route number (int).

    Returns:
        A tuple with the following three values:
        - SR: A three-digit number, padded with zeroes if necessary.
        - RRT: Related Route Type. Will be None if not applicable to input route_id
        - RRQ: Related Route Qualifier. Will be None if not applicable to input
            route_id and will always be None if RRT is None.

    Raises:
        SRFormatError: raised if the route_id cannot be parsed.
    """
    # Convert integer to three-digit route ID.
    if isinstance(route_id, int):
        return ("%03d" % route_id, None, None)
    # Convert non-string to string.
    if not isinstance(route_id, str):
        route_id = str(route_id)

    if re.match(r"^\d{1,2}$", route_id):
        return ("%03d" % int(route_id), None, None)

    match = _ROUTE_ID_RE.match(route_id)
    if not match:
        raise SRFormatError(route_id)
    else:
        parts = map(match.group, ("sr", "rrt", "rrq"))
        return tuple(parts)
