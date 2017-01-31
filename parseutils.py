'''Utilities for parsing strings into other types.
'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import re

_DATE_RE = re.compile(r"\/Date\((\d+)([+\-]\d+)\)\/", re.IGNORECASE)
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


def parse_date(wcf_date):
    """Parses a WCF serialzied date to a date string.
    :param wcf_date: A date/time in WCF JSON serialized format.
    :type wcf_date: str
    :rtype: datetime.datetime
    """
    if wcf_date:
        match = _DATE_RE.match(wcf_date)
        if match:
            groups = match.groups()
            ticks = None
            if len(groups) >= 2:
                ticks = (int(groups[0]) + int(groups[1])) / 1000
            else:
                ticks = int(groups[0]) / 1000
            return datetime.datetime.fromtimestamp(ticks)
        else:
            return wcf_date


def split_camel_case(the_string):
    """Splits a camel case word into individual words separated by spaces
    :param the_string: A camel-case word.
    :type the_string: str
    :rtype: str
    """
    if the_string is not None:
        words = _CAMEL_CASE_RE.findall(the_string)
        return " ".join(words)
    else:
        return None


def parse_route_id(route_id):
    """Parses a route identifier into its component parts: SR, RRT, RRQ
    """
    if not isinstance(route_id, (unicode, str)):
        raise TypeError("route_id should be a str or unicode")
    if re.match(r"^\d{1,3}$", route_id):
        if len(route_id) == 1:
            return "00%s" % route_id, None, None
        elif len(route_id) == 2:
            return "0%s" % route_id, None, None
        else:
            return route_id, None, None
    match = _ROUTE_ID_RE.match(route_id)
    if not match:
        raise SRFormatError(route_id)
    if match:
        return tuple(map(match.group, ("sr", "rrt", "rrq")))
