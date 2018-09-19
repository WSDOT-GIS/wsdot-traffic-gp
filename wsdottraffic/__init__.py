'''wsdottraffic
Returns data from the WSDOT Traveler Info REST endpoints.
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
import os
import re
import sys
from sys import version_info

from .jsonhelpers import CustomEncoder, parse_traveler_info_object
from .resturls import URLS

# Choose correct library for Python version
if version_info.major <= 2:
    # pylint:disable=import-error,unused-import
    from urllib2 import urlopen, HTTPError, Request
else:
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError

# Get default access code
ENVIRONMENT_VAR_NAME = "WSDOT_TRAFFIC_API_CODE"
if ENVIRONMENT_VAR_NAME in os.environ:
    _DEFAULT_ACCESS_CODE = os.environ[ENVIRONMENT_VAR_NAME]
else:
    _DEFAULT_ACCESS_CODE = None


_NO_CODE_MESSAGE = "No access code provided. Must be provided either by parameter or WSDOT_TRAFFIC_API_CODE environment variable."


def get_traveler_info_json(dataname, accesscode=_DEFAULT_ACCESS_CODE):
    # (str, str) -> bytes
    """Gets the highway alerts data from the REST endpoint.

    Args:
        dataname: str. The name of the traffic data set to retrieve.
        accesscode: str. Access code. (optional if default is provided.)

    Returns:
        bytes. The JSON output from the rest endpoint
    """
    if not accesscode:
        if _DEFAULT_ACCESS_CODE:
            accesscode = _DEFAULT_ACCESS_CODE
        else:
            raise TypeError(_NO_CODE_MESSAGE)
    url = "%s?AccessCode=%s" % (URLS[dataname], accesscode)
    with urlopen(url) as json_file:
        output = json_file.read()
    return output


def get_traveler_info(dataname, accesscode=_DEFAULT_ACCESS_CODE):
    # (str, str) -> List[dict]
    """Gets the highway alerts data from the REST endpoint.

    Args:
        dataname: str. The name of the traffic data set to retrieve.
        accesscode: str. Access code. (optional if default is provided.)

    Returns:
        Returns a list of dict objects.
    """
    if not accesscode:
        raise TypeError(_NO_CODE_MESSAGE)
    url = "%s?AccessCode=%s" % (URLS[dataname], accesscode)
    json_response = urlopen(url)
    json_txt = json_response.read()
    if not isinstance(json_txt, str):
        json_txt = str(json_txt, "utf-8")
    json_data = json.loads(json_txt,
                           object_hook=parse_traveler_info_object)
    del json_response
    return json_data
