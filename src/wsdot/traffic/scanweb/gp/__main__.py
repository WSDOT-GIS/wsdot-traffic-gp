from __future__ import print_function, absolute_import, unicode_literals
import argparse
from os.path import split, abspath
from . import populate_feature_classes
import arcpy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gdb", help="The output file geodatabase.")
    parser.add_argument("template_gdb", help="File geodatabase containing templates for feature class and table creation.", nargs="?")
    args = parser.parse_args()
    gdb = args.gdb
    gdb = abspath(gdb)

    if not arcpy.Exists(gdb):
        arcpy.management.CreateFileGDB(*split(gdb))
    populate_feature_classes(gdb)

if __name__ == '__main__':
    main()
