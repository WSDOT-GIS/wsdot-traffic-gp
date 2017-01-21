"""Unit test for travelerinfo
"""

import unittest, travelerinfo
from resturls import urls

class TestTravelerInfo(unittest.TestCase):
    """Defines a unit test test case
    """
    def perform_basic_tests(self, the_list):
        """Performs tests common to all of the returned lists."""
        self.assertIsInstance(the_list, list)
        self.assertGreater(len(the_list), 0)
        for c in the_list:
            self.assertIsInstance(c, dict)
    def test_endpoints(self):
        # Call the REST endpoints and store results.
        for k in urls:
            ds = travelerinfo.getTravelerInfo(k)
            self.perform_basic_tests(ds)
if __name__ == '__main__':
    unittest.main()