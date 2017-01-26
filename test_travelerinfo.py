"""Unit test for travelerinfo
"""

import unittest
import travelerinfo
from resturls import URLS


class TestTravelerInfo(unittest.TestCase):
    """Defines a unit test test case
    """
    def perform_basic_tests(self, the_list):
        """Performs tests common to all of the returned lists."""
        self.assertIsInstance(the_list, list)
        self.assertGreater(len(the_list), 0)
        for current in the_list:
            self.assertIsInstance(current, dict)

    def test_endpoints(self):
        """Tests the rest endpoints.
        """
        # Call the REST endpoints and test them.
        for k in URLS:
            dataset = travelerinfo.get_traveler_info(k)
            self.perform_basic_tests(dataset)
if __name__ == '__main__':
    unittest.main()
