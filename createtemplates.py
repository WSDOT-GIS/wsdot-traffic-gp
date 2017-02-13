"""
Creates the templates file geodatabase.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
from os import path

import arcpy
from wsdottraffic.gp import TABLE_DEFS_DICT_DICT, create_table

if __name__ == '__main__':
    # Get the .. directory
    DATA_DIR = path.abspath("Data")

    # Create the data dir if it does not exist already.
    if not path.exists(DATA_DIR):
        arcpy.AddMessage("Creating directory, %s..." % DATA_DIR)
        os.mkdir(DATA_DIR)
    else:
        arcpy.AddMessage("%s already exists.  Skipping creation step." %
                         DATA_DIR)

    # Create the Templates GDB
    arcpy.env.overwriteOutput = True
    GDB_NAME = "Templates.gdb"
    GDB_PATH = path.join(DATA_DIR, GDB_NAME)
    arcpy.AddMessage("Creating %s..." % GDB_PATH)
    arcpy.management.CreateFileGDB(DATA_DIR, GDB_NAME)
    for key in TABLE_DEFS_DICT_DICT:
        arcpy.AddMessage("Creating %s in %s..." % (key, GDB_PATH))
        create_table(path.join(GDB_PATH, key))
    arcpy.AddMessage("Completed")
