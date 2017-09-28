from __future__ import print_function, absolute_import, unicode_literals
import argparse
from os.path import split, abspath
from . import populate_feature_classes
from ... import _DEFAULT_ACCESS_CODE
import arcpy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gdb")
    args = parser.parse_args()
    gdb = args.gdb
    gdb = abspath(gdb)

    if not arcpy.Exists(gdb):
        arcpy.management.CreateFileGDB(*split(gdb))
    populate_feature_classes(gdb)

if __name__ == '__main__':
    main()