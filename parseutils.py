'''Utilities for parsing strings into other types.
'''
import datetime
import re

dateRe = re.compile(r"\/Date\((\d+)([+\-]\d+)\)\/",re.IGNORECASE)
camelCaseRe = re.compile(r"(?:[A-Z][a-z]+)|[A-Z]{2}")

def parseDate(wcfDate):
    """Parses a WCF serialzied date to a date string.
    @param wcfDate: A date/time in WCF JSON serialized format.
    @type wcfDate: str
    @rtype: datetime.datetime
    """
    if wcfDate:
        match = dateRe.match(wcfDate)
        if match:
            groups = match.groups()
            ticks = None
            if (len(groups) >= 2):
                ticks = (int(groups[0]) + int(groups[1])) / 1000
            else:
                ticks = int(groups[0]) / 1000
            return datetime.datetime.fromtimestamp(ticks)
        else:
            return wcfDate

def splitCamelCase(s):
    """Splits a camel case word into individual words separated by spaces
    @param s: A camel-case word.
    @type s: str
    @rtype: str
    """
    if (s is not None):
        words = camelCaseRe.findall(s)
        return str.join(" ", words)
    else:
        return None