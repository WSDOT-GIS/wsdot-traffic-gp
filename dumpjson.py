'''dumpjson
Returns data from the WSDOT Traveler Info REST endpoints.
'''

import os
import json
import logging
from argparse import ArgumentParser

from wsdottraffic import (URLS, _DEFAULT_ACCESS_CODE,
                          get_traveler_info, ENVIRONMENT_VAR_NAME)
from wsdottraffic.jsonhelpers import CustomEncoder
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
    data_dict = {}
    fields_dict = {}
    for endpoint_name in URLS:
        # Get the features via the API.
        features = get_traveler_info(endpoint_name, CODE)
        data_dict[endpoint_name] = features
        # Extract field definitions
        fields = FieldInfo.from_features(features)
        fields_dict[endpoint_name] = fields

    # Dump features to JSON file
    out_path = os.path.join(OUTDIR, "data.json")
    with open(out_path, 'w') as json_file:
        json.dump(data_dict, json_file, cls=CustomEncoder, indent=True)

    # Dump field defs. to JSON file
    out_path = os.path.join(OUTDIR, "fields.json")
    with open(out_path, "w") as json_file:
        json.dump(
            fields_dict, json_file, indent=True, default=_field_serializer
        )

if __name__ == '__main__':
    main()
