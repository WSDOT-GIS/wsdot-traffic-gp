"""
Updates a feature collection
"""
from os.path import exists
import json
from arcgis.gis import GIS, Item
from arcgis.features import FeatureCollection
from arcgis.features.manage_data import extract_data

_LOGIN_JSON_PATH = "login-info.json"


def main():
    if not exists(_LOGIN_JSON_PATH):
        raise FileNotFoundError(_LOGIN_JSON_PATH)

    # Read login parameters from JSON file.
    with open(_LOGIN_JSON_PATH) as login_info_file:
        login_info = json.load(login_info_file)

    # Specify the title that this script will either update or create.

    gis = GIS(**login_info)
    hosted_layer_item = Item(gis, "9aa00fafb8fd49e59fef5fc995b75f8c")
    print("$s" % hosted_layer_item)
    feature_collection_item = Item(gis, "74f750d8e7d74db08cf4b133d3edc7f0")
    print("$s", feature_collection_item)
    # Everything above this line works correctly.

    # TODO: Export the hosted feature layer to feature collection,
    # overwriting existing feature collection if present.

    # See http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Export_Item/02r30000008s000000/

    """
    POST http://wsdot.maps.arcgis.com/sharing/rest/content/users/[user_name]/export HTTP/1.1
    Host: wsdot.maps.arcgis.com
    Connection: keep-alive
    Content-Length: 298
    Origin: http://wsdot.maps.arcgis.com
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36
    Content-Type: application/x-www-form-urlencoded
    Accept: */*
    Referer: http://wsdot.maps.arcgis.com/home/item.html?id=[item_id]
    Accept-Encoding: gzip, deflate
    Accept-Language: en-US,en;q=0.8
    Cookie: [removed]

    itemId=[item_id]&title=TravelerInfo&exportFormat=Feature%20Collection&f=json&token=[token_removed]
    HTTP/1.1 200 OK
    Access-Control-Allow-Credentials: true
    Access-Control-Allow-Origin: http://wsdot.maps.arcgis.com
    Cache-Control: no-cache
    Content-Encoding: gzip
    Content-Type: text/plain;charset=utf-8
    Date: Fri, 10 Mar 2017 00:33:50 GMT
    Expires: -1
    Pragma: no-cache
    Vary: Origin
    Vary: Accept-Encoding, User-Agent
    Content-Length: 231
    Connection: keep-alive
    """

    # gis.py/_GISResource has token property.

    f_coll = FeatureCollection.fromitem(hosted_layer_item)
    extract_data(f_coll)
    pass


if __name__ == '__main__':
    main()
