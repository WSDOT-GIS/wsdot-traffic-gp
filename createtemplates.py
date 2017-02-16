"""
Creates the templates file geodatabase.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
from os import path
import logging

import arcpy
from wsdottraffic.gp import TABLE_DEFS_DICT_DICT, create_table

if __name__ == '__main__':
    # Get the .. directory
    DATA_DIR = path.abspath("Data")

    # Create the data dir if it does not exist already.
    if not path.exists(DATA_DIR):
        logging.info("Creating directory, %(dir)s...", {"dir": DATA_DIR})
        os.mkdir(DATA_DIR)
    else:
        logging.info("%(dir)s already exists.  Skipping creation step.",
                     {"dir": DATA_DIR})

    # Create the Templates GDB
    arcpy.env.overwriteOutput = True
    GDB_NAME = "Templates.gdb"
    GDB_PATH = path.join(DATA_DIR, GDB_NAME)
    MSG_DICT = {"gdb_path": GDB_PATH}
    logging.info("Creating %(gdb_path)s...", MSG_DICT)
    arcpy.management.CreateFileGDB(DATA_DIR, GDB_NAME)
    for key in TABLE_DEFS_DICT_DICT:
        MSG_DICT["table_name"] = key
        logging.info("Creating %(table_name)s in %(gdb_path)s...", MSG_DICT)
        create_table(path.join(GDB_PATH, key))
    logging.info("Completed")
