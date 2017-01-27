'''Utilities for parsing strings into other types.
'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import re

_DATE_RE = re.compile(r"\/Date\((\d+)([+\-]\d+)\)\/", re.IGNORECASE)
_CAMEL_CASE_RE = re.compile(r"(?:[A-Z][a-z]+)")


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
