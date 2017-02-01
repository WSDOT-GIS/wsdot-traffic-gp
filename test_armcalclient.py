"""Test for armcalcclient
"""

import unittest
from datetime import date
from armcalcclient import ArmCalcInput, ArmCalcClient


class TestArmCalc(unittest.TestCase):
    """Defines a unit test case for testing armcalcclient
    """

    def test_batch(self):
        """Test batch conversion
        """
        the_date = date(2014, 8, 19)

        input_list = [
            {"CalcType": 1, "SR": "005", "ReferenceDate": the_date,
             "ARM": 0.32, "ResponseDate": the_date},
            {"CalcType": 0, "SR": "005", "ReferenceDate": the_date,
             "SRMP": 150.0, "ResponseDate": the_date}
            ]
        data = []
        for item in input_list:
            aci = ArmCalcInput(**item)
            data.append(aci)
        client = ArmCalcClient()
        result = client.batch(data)

        with open("results.json", "w") as out_file:
            out_file.write(result)

if __name__ == "__main__":
    unittest.main()
