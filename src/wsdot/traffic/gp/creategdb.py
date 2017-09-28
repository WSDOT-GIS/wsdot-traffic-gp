"""creategdb
Queries the WSDOT Traveler Info REST endpoints and populates a table using the
results.

Parameters:
0   Workspace.  Optional.  Defaults to ./TravelerInfo.gdb.
1   Access Code. Optional if provided via environment variable.
2   Templates GDB. Optional Defaults to "./Data/Templates.gdb"
3   Templates GDB (output)
"""
from __future__ import absolute_import, print_function, unicode_literals
import os
import logging
import argparse

import arcpy

from .. import URLS, get_traveler_info
from . import create_table

_LOGGER = logging.getLogger(__name__)


def main():
    """Uses this when run as a script
    """
    default_gdb_path = "./TravelerInfo.gdb"
    api_code_var_name = "WSDOT_TRAFFIC_API_CODE"
    api_code = os.environ.get(api_code_var_name)

    parser = argparse.ArgumentParser(
        description="Creates a file geodatabase using data from the WSDOT Traffic API.")

    parser.add_argument("--gdb-path", type=str, default=default_gdb_path,
                        help='Path to where the GDB will be created. Defaults to "%s".' % default_gdb_path,
                        nargs="?")
    parser.add_argument("--templates-gdb", help="Path to GDB with template feature classes. (Creating feature classes with templates is faster than using the Add Field tool.)")
    p_help = "WSDOT Traffic API code. Defaults to value of %s environment variable if available. If this environment variable does not exist, then this parameter is required." % api_code_var_name
    parser.add_argument("--code", "-c", type=str,
                        required=api_code is None, default=api_code,
                        help=p_help)

    default_names = [
        "CVRestrictions",
        "HighwayAlerts",
        "HighwayCameras",
        "MountainPassConditions",
        "TrafficFlow",
        "WeatherInformation",
        "TravelTimes"
    ]

    p_help = 'One or more of the following values: %s' % set(URLS.keys())

    parser.add_argument("names", type=str, nargs=argparse.REMAINDER, help=p_help)

    args = parser.parse_args()
    if not args.names:
        names = default_names
    else:
        names = args.names

    templates_gdb = args.templates_gdb
    create_gdb(args.gdb_path, args.code, templates_gdb, names)


def create_gdb(out_gdb_path="./TravelerInfo.gdb", access_code=None,
               templates_gdb=None, names=(
                   "CVRestrictions",
                   "HighwayAlerts",
                   "HighwayCameras",
                   "MountainPassConditions",
                   "TrafficFlow",
                   "WeatherInformation",
                   "TravelTimes"
               )):
    """Creates a file geodatabase of traffic API info"""

    # Create the file GDB if it does not already exist.
    arcpy.env.overwriteOutput = True
    if not arcpy.Exists(out_gdb_path):
        _LOGGER.debug("Creating GDB")
        arcpy.management.CreateFileGDB(*os.path.split(out_gdb_path))

    # Download each of the REST endpoints.
    for name in names:
        print("Contacting %s..." % URLS[name])
        # If user provided access code, use it.
        # Otherwise don't provide to function, which will use default from
        # environment or text file.`
        if access_code:
            data = get_traveler_info(name, access_code)
        else:
            data = get_traveler_info(name)
        out_table = os.path.join(out_gdb_path, name)
        create_table(out_table, None, data, templates_gdb)

if __name__ == '__main__':
    main()
