"""creategdb
Queries the WSDOT Traveler Info REST endpoints and populates a table using the
results.

Parameters:
0   Workspace.  Optional.  Defaults to ./TravelerInfo.gdb.
1   Access Code. Optional if provided via environment variable.
2   Templates GDB. Optional Defaults to "./Data/Templates.gdb"
3   Templates GDB (output)
"""
import os
import zipfile
import logging

import arcpy

from wsdottraffic import URLS, get_traveler_info
from wsdottraffic.gp import create_table

logging.getLogger(__name__)


def main(out_gdb_path="./TravelerInfo.gdb", access_code=None,
         templates_gdb=None, names=(
             "CVRestrictions",
             "HighwayAlerts",
             "HighwayCameras",
             "MountainPassConditions",
             "TrafficFlow",
             "WeatherInformation",
             "TravelTimes"
         )):
    """Uses this when run as a script
    """

    # Create the file GDB if it does not already exist.
    arcpy.env.overwriteOutput = True
    if not arcpy.Exists(out_gdb_path):
        logging.debug("Creating GDB")
        arcpy.management.CreateFileGDB(*os.path.split(out_gdb_path))

    # Download each of the REST endpoints.
    for name in names:
        logging.info("Contacting %(url)s...", {"url": URLS[name]})
        # If user provided access code, use it.
        # Otherwise don't provide to function, which will use default from
        # environment or text file.`
        if access_code:
            data = get_traveler_info(name, access_code)
        else:
            data = get_traveler_info(name)
        out_table = os.path.join(out_gdb_path, name)
        create_table(out_table, None, data, templates_gdb)
    logging.info("Compressing data in %(out_gdb_path)s...",
                 {"out_gdb_path":  out_gdb_path})

    zip_path = "%s.zip" % out_gdb_path
    logging.info("Creating %(zip_path)s...", {"zip_path", zip_path})
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w") as out_zip:
        logging.info("Adding files to zip...")
        for dirpath, dirnames, filenames in os.walk(out_gdb_path):
            del dirnames
            for file_name in filenames:
                out_path = os.path.join(dirpath, file_name)
                out_zip.write(out_path)


if __name__ == '__main__':
    # Get the parameters or set default values.
    ARG_COUNT = arcpy.GetArgumentCount()
    ARGS_DICT = {}
    # Set default output path
    # Use user-provided output path if available.
    if ARG_COUNT > 0:
        ARGS_DICT["out_gdb_path"] = arcpy.GetParameterAsText(0)
    # Get the API access code
    if ARG_COUNT > 1:
        ARGS_DICT["access_code"] = arcpy.GetParameterAsText(1)
    # Get the geodatabase containing templates
    if ARG_COUNT > 2:
        TEMPLATES_GDB = arcpy.GetParameterAsText(2)
        if arcpy.Exists(TEMPLATES_GDB):
            ARGS_DICT["templates_gdb"] = TEMPLATES_GDB
    main(**ARGS_DICT)
