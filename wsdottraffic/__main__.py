'''dumpjson
Returns data from the WSDOT Traveler Info REST endpoints.
'''
from __future__ import unicode_literals, absolute_import, print_function, division
import sys
import os
import json
import logging
from argparse import ArgumentParser

import geojson

from . import (URLS, _DEFAULT_ACCESS_CODE,
               get_traveler_info, get_traveler_info_json,
               ENVIRONMENT_VAR_NAME)
from .fielddetection import FieldInfo
from .classes import TrafficJSONEncoder


def _field_serializer(the_object):
    if isinstance(the_object, FieldInfo):
        return the_object.__dict__
    return the_object


CODE = _DEFAULT_ACCESS_CODE
OUTDIR = "output"

logging.getLogger(__name__)

# class CustomGeoJSONEncoder(json.JSONEncoder):
#     def default(self, o): # pylint:disable=method-hidden
#         if "__geo_interface__" in dir(o):
#             return o.__geo_interface__
#         return super().default(o)


def main():
    """Main function. Runs when called as a script.
    """
    arg_parser = ArgumentParser(
        description="Dumps data from the WSDOT Traffic API to JSON files.")
    arg_parser.add_argument(
        "--raw", action="store_true",
        help="Dumps unprocessed JSON output from services")
    arg_parser.add_argument(
        "--geojson", action="store_true",
        help="Exports to GeoJSON format"
    )
    arg_parser.add_argument(
        "api_code", nargs="?",
        help="WSDOT Traveler API code. This parameter can be omitted if the %s environment variable is defined." % ENVIRONMENT_VAR_NAME)  # pylint:disable=line-too-long
    args = arg_parser.parse_args()
    api_code = args.api_code
    if not api_code:
        api_code = _DEFAULT_ACCESS_CODE
    # Create the output directory if not already present.
    if not os.path.exists(OUTDIR):
        os.mkdir(OUTDIR)
    for endpoint_name in URLS:
        if args.raw:
            raw_json = get_traveler_info_json(endpoint_name, api_code)
            with open(os.path.join(OUTDIR, "%s_raw.json" % endpoint_name), "wb") as json_file:
                json_file.write(raw_json)
            continue
        # Get the features via the API.
        features = get_traveler_info(endpoint_name, api_code)
        # Extract field definitions

        ext = "json"
        if args.geojson:
            ext = "geojson"

        # Write data and field info to JSON files.
        out_path = os.path.join(OUTDIR, "%s.%s" % (endpoint_name, ext))
        with open(out_path, 'w') as json_file:
            if args.geojson:
                feature_collection = geojson.factory.FeatureCollection(features)
                try:
                    geojson.dump(feature_collection, json_file, indent=True)
                    # json.dump(features, json_file, cls=CustomGeoJSONEncoder, indent=True)
                except:
                    print("Error dumping %s" % endpoint_name, file=sys.stderr)
                    raise
            else:
                json.dump(features, json_file, cls=TrafficJSONEncoder, indent=True)


if __name__ == '__main__':
    main()
