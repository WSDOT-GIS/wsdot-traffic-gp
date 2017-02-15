'''dumpjson
Returns data from the WSDOT Traveler Info REST endpoints.
@author: Jeff Jacobson

Parameters:
1    data name
2    WSDOT Traffic API access code (optional if default is set via
     WSDOT_TRAFFIC_API_CODE environment variable.)
'''

import sys
import re
import os
import json

from wsdottraffic import (URLS, _DEFAULT_ACCESS_CODE,
                          get_traveler_info)
from wsdottraffic.jsonhelpers import CustomEncoder

# Check parameters. Note that parameter 0 is this script's name.

if len(sys.argv) < 2:
    # Create list of valid values for error message.
    VALID_KEYS = list(URLS.keys())
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
        OUTDIR = "output"
        # Create the output directory if not already present.
        if not os.path.exists(OUTDIR):
            os.mkdir(OUTDIR)
        for endpoint_name in URLS:
            with open("%s/%s.json" % (OUTDIR, endpoint_name), 'w') as f:
                json.dump(get_traveler_info(endpoint_name, CODE), f,
                          cls=CustomEncoder, indent=True)
    else:
        json.dump(get_traveler_info(NAME, CODE), sys.stdout,
                  cls=CustomEncoder, indent=True)
