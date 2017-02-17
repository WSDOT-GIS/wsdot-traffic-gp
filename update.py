"""Logs into ArcGIS Online and updates a feature collection.
Requires ArcGIS Pro installation to supply arcpy module
"""

import json
from sys import stderr
from os.path import exists
import re

from arcgis.gis import GIS
import creategdb

_GDB_PATH = "TravelerInfo.gdb.zip"
_LOGIN_JSON_PATH = "login-info.json"
GDB_TITLE = "TravelerApi"
FOLDER = "TravelerInfo"


def main():
    """Main function executed when script is run
    """
    if not exists(_LOGIN_JSON_PATH):
        raise FileNotFoundError(_LOGIN_JSON_PATH)
    else:
        stderr.write("%s\n" % "Creating or updating GDB")
        # Create or update the file geodatabase.
        creategdb.main()

    if not exists(_GDB_PATH):
        raise FileNotFoundError(_GDB_PATH)

    # Read login parameters from JSON file.
    with open(_LOGIN_JSON_PATH) as login_info_file:
        login_info = json.load(login_info_file)

    # Specify the title that this script will either update or create.

    gis = GIS(**login_info)

    search_results = gis.content.search(
        query="%s owner:%s" % (GDB_TITLE, gis.properties.user.username),
        item_type="File Geodatabase")

    if len(search_results) <= 0:
        try:
            tags = ("WSDOT", "traffic", "traveler", "transportation")
            traffic_gdb_item = gis.content.add({
                "title": GDB_TITLE,
                "type": "File Geodatabase",
                "tags": ",".join(tags),
                "culture": "en-US"
            }, data=_GDB_PATH, folder=FOLDER)
        except RuntimeError as ex:
            stderr.write("Error uploading zipped file GDB.\n\t%s\n" % ex)
            exit("%s" % ex)

        try:
            traffic_gdb_item.publish()
        except Exception as ex:  # pylint:disable=broad-except
            # The publish function throws just a regular old Exception
            # if it fails. Check the message it has returned to see if it is
            # on of the expected error messages.
            match = re.match(
                r"Job (?:(?:failed)|(?:cancelled)|(?:timed out)).",
                ex.args[0], re.IGNORECASE)
            if match:
                stderr.write("Error publishing GDB as service:\n\t%s\n" %
                             match.group(0))
                exit("%s" % ex)
            else:
                # re-raise the exception if it is not one of the expected error
                # messages
                raise

    else:
        print("items found")
        # Print list of items, one per line.
        print("\n\n".join(map(
            lambda sitem: "%s" % sitem, search_results)))
        # Upload zipped GDB to update the existing content.
        if len(search_results) == 1:
            gdb_item = search_results[0]
            print("Updating %s by uploading %s..." % (
                gdb_item.title, _GDB_PATH))
            gdb_item.update(data=_GDB_PATH)


if __name__ == '__main__':
    main()
