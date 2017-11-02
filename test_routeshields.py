"""Test for routeshields
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import unittest
from wsdottraffic.routeshields import id_to_label, label_to_3_digit_id


class RouteShieldsTest(unittest.TestCase):
    """Defines test case
    """

    def test_routeshields(self):
        """Defines unit test
        """
        self.assertEqual(id_to_label("005"), "I-5")
        self.assertEqual(label_to_3_digit_id("I-5"), "005")

if __name__ == '__main__':
    unittest.main()
