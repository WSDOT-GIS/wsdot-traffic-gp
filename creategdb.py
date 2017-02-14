"""creategdb
Queries the WSDOT Traveler Info REST endpoints and populates a table using the
results.

Parameters:
0   Workspace.  Optional.  Defaults to ./TravelerInfo.gdb.
1   Access Code. Optional if provided via environment variable.
2   Templates GDB. Optional Defaults to "./Data/Templates.gdb"
3   Templates GDB (output)
"""
import sys
import os
import zipfile
import arcpy

from wsdottraffic import URLS, get_traveler_info
from wsdottraffic.gp import create_table

# Get the parameters or set default values.
ARG_COUNT = arcpy.GetArgumentCount()
# Set default output path
OUT_GDB_PATH = "./TravelerInfo.gdb"
# Use user-provided output path if available.
if ARG_COUNT > 0:
    OUT_GDB_PATH = arcpy.GetParameterAsText(0)
# Get the API access code
ACCESS_CODE = None
if ARG_COUNT > 1:
    ACCESS_CODE = arcpy.GetParameterAsText(1)
# Get the geodatabase containing templates
TEMPLATES_GDB = "Data/Templates.gdb"
if ARG_COUNT > 2:
    TEMPLATES_GDB = arcpy.GetParameterAsText(2)
# If the templates GDB doesn't exist, set variable to None.
if not arcpy.Exists(TEMPLATES_GDB):
    TEMPLATES_GDB = None

# Create the file GDB if it does not already exist.
arcpy.env.overwriteOutput = True
if not arcpy.Exists(OUT_GDB_PATH):
    arcpy.management.CreateFileGDB(*os.path.split(OUT_GDB_PATH))

# Download each of the REST endpoints.
for name in URLS:
    arcpy.AddMessage("Contacting %s..." % URLS[name])
    # If user provided access code, use it.
    # Otherwise don't provide to function, which will use default from
    # environment or text file.`
    if ACCESS_CODE:
        data = get_traveler_info(name, ACCESS_CODE)
    else:
        data = get_traveler_info(name)
    OUT_TABLE = os.path.join(OUT_GDB_PATH, name)
    create_table(OUT_TABLE, None, data, TEMPLATES_GDB)
sys.stderr.write("Compressing data in %s" % OUT_GDB_PATH)

ZIP_PATH = "%s.zip" % OUT_GDB_PATH
sys.stderr.write("Creating %s..." % ZIP_PATH)
if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)
with zipfile.ZipFile(ZIP_PATH, "w",
                     zipfile.ZIP_LZMA) as out_zip:
    sys.stderr.write("Adding files to zip...")
    for dirpath, dirnames, filenames in os.walk(OUT_GDB_PATH):
        for fn in filenames:
            out_path = os.path.join(dirpath, fn)
            out_zip.write(out_path, fn)

arcpy.SetParameterAsText(3, OUT_GDB_PATH)
