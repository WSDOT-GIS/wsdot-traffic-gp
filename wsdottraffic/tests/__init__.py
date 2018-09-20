"""Unit test for wsdottraffic
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest
import os
import re
import json
from wsdottraffic import get_traveler_info
from wsdottraffic.classes import TrafficJSONEncoder, parse
from wsdottraffic.resturls import URLS
from wsdottraffic.routeshields import id_to_label, label_to_3_digit_id
from wsdottraffic.dicttools import flatten_dict


# class TestTravelerInfo(unittest.TestCase):
#     """Defines a unit test test case
#     """

#     def perform_basic_tests(self, the_list):
#         """Performs tests common to all of the returned lists."""
#         self.assertIsInstance(the_list, list)
#         self.assertGreater(len(the_list), 0)
#         for current in the_list:
#             self.assertIsInstance(current, dict)

#     def test_endpoints(self):
#         """Tests the rest endpoints.
#         """
#         # Call the REST endpoints and test them.
#         for k in URLS:
#             dataset = get_traveler_info(k)
#             self.perform_basic_tests(dataset)


class RouteShieldsTest(unittest.TestCase):
    """Defines test case
    """

    def test_routeshields(self):
        """Defines unit test
        """
        self.assertEqual(id_to_label("005"), "I-5")
        self.assertEqual(label_to_3_digit_id("I-5"), "005")


class ClassTest(unittest.TestCase):

    def test_flatten_dict(self):
        data = {
            "FlowDataID": 2482,
            "FlowReadingValue": 1,
            "FlowStationLocation": {
                "Description": "Homeacres Rd",
                "Direction": "EB",
                "Latitude": 47.978415632,
                "Longitude": -122.174701738,
                "MilePost": 0.68,
                "RoadName": "002"
            },
            "Region": "Northwest",
            "StationName": "002es00068",
            "Time": "/Date(1536618682000-0700)/"
        }

        flat_dict = dict(flatten_dict(data))
        expected_output = {
            "FlowDataID": 2482,
            "FlowReadingValue": 1,
            "FlowStationLocationDescription": "Homeacres Rd",
            "FlowStationLocationDirection": "EB",
            "FlowStationLocationLatitude": 47.978415632,
            "FlowStationLocationLongitude": -122.174701738,
            "FlowStationLocationMilePost": 0.68,
            "FlowStationLocationRoadName": "002",
            "Region": "Northwest",
            "StationName": "002es00068",
            "Time": "/Date(1536618682000-0700)/"
        }

        self.assertDictEqual(flat_dict, expected_output)

        dict_key: str = None
        for key, val in expected_output.items():
            if isinstance(val, dict):
                dict_key = key
                break

        self.assertIsNone(dict_key, "should not have nested dict. '%s'" % dict_key)

    def test_deserialize(self):

        # Read JSON files and deserialize
        jsondir = os.path.dirname(__file__)
        jsondir = os.path.join(jsondir, "testjson")
        output = {}
        regex = re.compile(r"(\w+)_raw.json")
        for dirpath, dirnames, filenames in os.walk(jsondir):
            del dirnames
            for filename in filenames:
                jsonpath = os.path.join(dirpath, filename)
                key = regex.match(filename).groups()[0]
                with open(jsonpath, "r", encoding="utf_8") as json_file:
                    val = json.load(json_file, object_hook=parse)
                    output[key] = val
                self.assertIsNotNone(val)

        # Write the objects to files
        outdir = os.path.join(os.path.dirname(__file__), "testdump")
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        for key, val in output.items():
            self.assertGreater(len(val), 0)
            outfn = os.path.join(outdir, key + ".json")
            with open(outfn, "w", encoding='utf_8') as json_file:
                # f.write("%s" % l)
                json.dump(val, json_file, cls=TrafficJSONEncoder)


if __name__ == '__main__':
    unittest.main()
