"""
Creates the templates file geodatabase.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import os
from os import path
import logging

import arcpy
from . import TABLE_DEFS_DICT_DICT, create_table

_LOGGER = logging.getLogger(__name__)


def main():

    parser = argparse.ArgumentParser("Create templates feature class", None,
                                     "Create template feature classes")
    default_path = "Templates.gdb"
    parser.add_argument("template_gdb", help="Path where template file GDB will be created. Defaults to %s" % default_path,
                        default=default_path, nargs='?')
    parser.add_argument("--overwrite", action='store_true',
                        help='Overwrite existing filegeodatabase by deleting and recreating it.')

    args = parser.parse_args()

    # Create the Templates GDB
    gdb_path = args.template_gdb
    workspace, name = os.path.split(args.template_gdb)
    if not workspace:
        workspace = "."
    arcpy.env.overwriteOutput = args.overwrite

    if arcpy.env.overwriteOutput or not os.path.exists(gdb_path):
        print("Creating %s..." % gdb_path)
        arcpy.management.CreateFileGDB(workspace, name)
        for key in TABLE_DEFS_DICT_DICT:
            print("Creating %s in %s..." % (key, gdb_path))
            create_table(path.join(gdb_path, key))
    else:
        print('"%s" already exists and will not be recreated.' % gdb_path)
    _LOGGER.info("Completed")


if __name__ == '__main__':
    main()
