'''travelerinfo
Returns data from the WSDOT Traveler Info REST endpoints.
@author: Jeff Jacobson

Parameters:
1    data name
2    WSDOT Traffic API access code (optional if default is set via
     WSDOT_TRAFFIC_API_CODE environment variable or accesscode.txt file.)
'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
import os
import re
import sys
import urllib2

from jsonhelpers import CustomEncoder, parse_traveler_info_object
from resturls import URLS

# Get default access code
_ACCESS_CODE_FILENAME = "accesscode.txt"
_ENVIRONMENT_VAR_NAME = "WSDOT_TRAFFIC_API_CODE"
if os.path.exists(_ACCESS_CODE_FILENAME):
    with open(_ACCESS_CODE_FILENAME, "r") as ac_file:
        _DEFAULT_ACCESS_CODE = ac_file.read()
elif _ENVIRONMENT_VAR_NAME in os.environ:
    _DEFAULT_ACCESS_CODE = os.environ[_ENVIRONMENT_VAR_NAME]
else:
    _DEFAULT_ACCESS_CODE = None


_NO_CODE_MESSAGE = "No access code provided. Must be provided either by \
parameter or WSDOT_TRAFFIC_API_CODE enviroment variable."


def get_traveler_info_json(dataname, accesscode=_DEFAULT_ACCESS_CODE):
    """Gets the highway alerts data from the REST endpoint.
    @param dataname: The name of the traffic data set to retrieve.
    @type dataname: str
    @param accesscode: Access code. (optional if default is provided.)
    @type accesscode: str
    @return: The JSON output from the rest endpoint
    @rtype: list
    """
    if not accesscode:
        raise TypeError(_NO_CODE_MESSAGE)
    url = "%s?AccessCode=%s" % (URLS[dataname], accesscode)
    with urllib2.urlopen(url) as json_file:
        output = json_file.read()
    return output


def get_traveler_info(dataname, accesscode=_DEFAULT_ACCESS_CODE):
    """Gets the highway alerts data from the REST endpoint.
    @param dataname: The name of the traffic data set to retrieve.
    @type dataname: str
    @param accesscode: Access code. (optional if default is provided.)
    @type accesscode: str
    @return: Returns a list of dict objects.
    @rtype: list
    """
    if not accesscode:
        raise TypeError(_NO_CODE_MESSAGE)
    url = "%s?AccessCode=%s" % (URLS[dataname], accesscode)
    json_file = urllib2.urlopen(url)
    json_data = json.load(json_file, object_hook=parse_traveler_info_object)
    del json_file
    return json_data


if __name__ == '__main__':
    # Check parameters. Note that parameter 0 is this script's name.

    if len(sys.argv) < 2:
        # Create list of valid values for error message.
        VALID_KEYS = list(URLS.iterkeys())
        VALID_KEYS.sort()
        sys.stderr.write(
            "You must provide the traffic api type as a parameter.\
Valid values are:\n\tALL\n")
        for k in VALID_KEYS:
            sys.stderr.write("\t%s\n" % k)
        exit(1)
    elif len(sys.argv) < 3 and _DEFAULT_ACCESS_CODE is None:
        sys.exit("No access code was provided")
    else:
        NAME = sys.argv[1]
        CODE = _DEFAULT_ACCESS_CODE
        if len(sys.argv) >= 3:
            CODE = sys.argv[2]
        if re.match("ALL", NAME, re.IGNORECASE):
            for endpoint_name in URLS:
                with open("%s.json" % endpoint_name, 'w') as f:
                    json.dump(get_traveler_info(endpoint_name, CODE), f,
                              cls=CustomEncoder, indent=True)
        else:
            json.dump(get_traveler_info(NAME, CODE), sys.stdout,
                      cls=CustomEncoder, indent=True)
