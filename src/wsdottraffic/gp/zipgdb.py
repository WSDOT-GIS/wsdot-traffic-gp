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
import zipfile
import logging
import argparse

_LOGGER = logging.getLogger(__name__)


def main():
    """Uses this when run as a script
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("gdb_path", help="Path to a file geodatabase")
    args = parser.parse_args()

    gdb_path = args.gdb_path


    print("Compressing data in %s..." % gdb_path)
    zip_path = "%s.zip" % gdb_path
    print("Creating %s..." % zip_path)
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w") as out_zip:
        print("Adding files to zip...")
        for dirpath, dirnames, filenames in os.walk(gdb_path):
            del dirnames
            for file_name in filenames:
                out_path = os.path.join(dirpath, file_name)
                out_zip.write(out_path)


if __name__ == '__main__':
    main()
