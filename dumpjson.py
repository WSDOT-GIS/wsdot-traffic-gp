'''dumpjson
Returns data from the WSDOT Traveler Info REST endpoints.
'''

import os
import json
import logging
from argparse import ArgumentParser

from wsdottraffic import (URLS, _DEFAULT_ACCESS_CODE,
                          get_traveler_info, ENVIRONMENT_VAR_NAME)
from wsdottraffic.jsonhelpers import CustomEncoder, dict_list_to_geojson
from wsdottraffic.fielddetection import FieldInfo


def _field_serializer(the_object):
    if isinstance(the_object, FieldInfo):
        return the_object.__dict__
    else:
        return the_object

CODE = _DEFAULT_ACCESS_CODE
OUTDIR = "output"

logging.getLogger(__name__)


def main():
    """Main function. Runs when called as a script.
    """
    arg_parser = ArgumentParser(
        description="Dumps data from the WSDOT Traffic API to JSON files.")
    arg_parser.add_argument(
        "api-code", nargs="?",
        help="WSDOT Traveler API code. This parameter can be omitted if the %s\
 environment variable is defined." % ENVIRONMENT_VAR_NAME)
    arg_parser.parse_args()
    # Create the output directory if not already present.
    if not os.path.exists(OUTDIR):
        os.mkdir(OUTDIR)
    for endpoint_name in URLS:
        # Get the features via the API.
        features = get_traveler_info(endpoint_name, CODE)
        # Extract field definitions
        fields = FieldInfo.from_features(features)

        # Write data and field info to JSON files.
        out_path = os.path.join(OUTDIR, "%s.json" % endpoint_name)
        with open(out_path, 'w') as json_file:
            json.dump(
                features, json_file, cls=CustomEncoder, indent=True)
        out_path = os.path.join(OUTDIR, "%s_fields.json" % endpoint_name)
        with open(out_path, 'w') as json_file:
            json.dump(
                fields, json_file, indent=True, default=_field_serializer)

        # dump geojson
        geojson = dict_list_to_geojson(features)
        out_path = os.path.join(OUTDIR, "%s.geojson" % endpoint_name)
        with open(out_path, 'w') as json_file:
            json.dump(
                geojson, json_file, cls=CustomEncoder, indent=True)
if __name__ == '__main__':
    main()
