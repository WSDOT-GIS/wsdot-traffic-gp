"""Logs into ArcGIS Online and updates a feature collection.
Requires ArcGIS Pro installation to supply arcpy module
"""

import json
from sys import stderr
from os.path import exists
from typing import Iterable

from arcgis.gis import GIS, Item
import creategdb

_GDB_PATH = "TravelerInfo.gdb.zip"
_LOGIN_JSON_PATH = "login-info.json"
GDB_TITLE = "TravelerApi"
FOLDER = "TravelerInfo"
TAGS = ("WSDOT", "traffic", "traveler", "transportation")


class PublishError(Exception):
    """An exception raised when publishing to AGOL fails.
    """

    def __init__(self, parent_ex: Exception):
        super().__init__(parent_ex.args)
        # match = re.match(
        #     r"Job (?:(?:failed)|(?:cancelled)|(?:timed out)).",
        #     parent_ex.args[0], re.IGNORECASE)


class MultipleResultsError(Exception):
    """Raised when a search is performed and more than one
    result is returned when only a singe result was expected.
    """

    def __init__(self, search_results: Iterable[Item]):
        self.search_results = search_results
        super().__init__(
            "Too many results. Only a single result was expected.")


class ItemAddFailError(Exception):
    """Raised when failing to add an item to the GIS.
    """

    def __init__(self, parent_ex: RuntimeError):
        super().__init__(parent_ex.args)


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

    # Create or get exising file GDB
    traffic_gdb_item = _find_file_gdb(gis)
    if not traffic_gdb_item:
        traffic_gdb_item = _add_new_gdb(gis)

    # Publish GDB to feature service or get exising service.
    feature_service = _find_feature_svc(gis)
    if not feature_service:
        try:
            feature_service = traffic_gdb_item.publish()
        except Exception as ex:
            # ArcGIS API throws a plain Exception, which is not recommended.
            raise PublishError(ex)
    else:
        print("Updating %s by uploading %s..." % (traffic_gdb_item.title,
                                                  _GDB_PATH))
        traffic_gdb_item.update(data=_GDB_PATH)

    # Create or update feature collection
    feature_collection_item = _find_feature_collection(gis)
    if feature_collection_item:
        feature_collection_item.update(data=feature_service.url)
    else:
        feature_collection_item = _add_new_feature_collection(
            gis, feature_service)


def _search(gis, item_type):
    search_results = gis.content.search(
        query="%s owner:%s" % (GDB_TITLE, gis.properties.user.username),
        item_type=item_type)
    if len(search_results) <= 0:
        return None
    elif len(search_results) == 1:
        return search_results[0]
    else:
        raise MultipleResultsError(search_results)


def _find_file_gdb(gis: GIS):
    return _search(gis, "Feature Layer")


def _find_feature_svc(gis: GIS):
    return _search(gis, "Feature Layer")


def _find_feature_collection(gis: GIS):
    return _search(gis, "Feature Collection")


def _add_new_gdb(gis: GIS):
    return _add_item(gis, "File Geodatabase", _GDB_PATH)


def _add_new_feature_collection(gis: GIS, feature_service):
    # TODO: this doesn't actually add the data. Figure out how to do so.
    return _add_item(gis, "Feature Collection", feature_service.url)


def _add_item(
        gis: GIS, item_type: str, data: str, folder: str=FOLDER) -> Item:
    try:
        new_item = gis.content.add({
            "title": GDB_TITLE,
            "type": item_type,
            "tags": ",".join(TAGS),
            "culture": "en-US"
        }, data=data, folder=folder)
    except (RuntimeError, AttributeError) as ex:
        raise ItemAddFailError(ex)
    return new_item

if __name__ == '__main__':
    main()
