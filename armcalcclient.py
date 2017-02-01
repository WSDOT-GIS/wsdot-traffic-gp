"""Client for calling ArmCalc web serivce
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import urllib2
import sys
from datetime import datetime, date
from json import JSONEncoder, dumps

from parseutils import to_wcf_date

# pylint: disable=invalid-name
# property names match those of API, which aren't what pylint prefers.

CALC_TYPE_SRMP_TO_ARM = 0
CALC_TYPE_ARM_TO_SRMP = 1


class ArmCalcJsonEncoder(JSONEncoder):
    """Custom JSON encoder for serializing ArmCalc objects
    to JSON.
    """
    def default(self, obj):  # pylint: disable=method-hidden
        """Provides custom handling for ArmCalcInput, ArmCalcOutput, and
        datetime.datetime. All other types will be passed to super.default.
        """
        if isinstance(obj, (ArmCalcInput, ArmCalcOutput)):
            return obj.__dict__
        elif isinstance(obj, (datetime, date)):
            return to_wcf_date(obj)
        return super(ArmCalcJsonEncoder, self).default(obj)


class ArmCalcInput(object):
    """ArmCalc input
    """

    def __init__(self, CalcType=CALC_TYPE_SRMP_TO_ARM, SR="", RRT="",
                 RRQ="", ABIndicator="", ReferenceDate=None, ARM=0,
                 SRMP=0, ResponseDate=None, TransId=None):
        """Creates a new instance
        """
        #  Calculation Type. 0 = SRMP to ARM, 1 = ARM to SRMP *
        self.CalcType = CalcType
        #  Three digit state route ID. *
        self.SR = SR
        #  Related Route Type *
        self.RRT = RRT
        #  Related Route Qualifier *
        self.RRQ = RRQ
        #  Ahead / Back indicator for SRMP. "A" or null, or "B" *
        self.ABIndicator = ABIndicator
        #  Input data collection date *
        self.ReferenceDate = ReferenceDate
        #  Accumulated Route Mileage. Actual measure *
        self.ARM = ARM
        #  State Route Milepost - Posted milepost. May not match actual measure
        # due to route adjustments over time. *
        self.SRMP = SRMP
        #  Output date. Use self to match an LRS publication date. *
        self.ResponseDate = ResponseDate
        #  Transaction ID. Use a unique ID with batch results. *
        self.TransId = TransId
        super(ArmCalcInput, self).__init__()


class ArmCalcOutput(ArmCalcInput):
    """ArmCalc output
    """

    def __init__(self, CalcType=CALC_TYPE_SRMP_TO_ARM, SR=None, RRT=None,
                 RRQ=None, ABIndicator=None, ReferenceDate=None, ARM=None,
                 SRMP=None, ResponseDate=None, TransId=None,
                 CalculationReturnCode=None, CalculationReturnMessage=None,
                 RealignmentDate=None):
        # Calculation return code.
        self.CalculationReturnCode = CalculationReturnCode
        # Calulation return message. Will not have value if return code is 0.
        self.CalculationReturnMessage = CalculationReturnMessage
        # Realignment date. Date that a route was last realigned.
        self.RealignmentDate = RealignmentDate
        super(ArmCalcOutput, self).__init__(CalcType, SR, RRT, RRQ,
                                            ABIndicator,
                                            ReferenceDate, ARM, SRMP,
                                            ResponseDate, TransId)

DEFAULT_URL = \
    "http://webapps.wsdot.loc/StateRoute/LocationReferencingMethod/\
Transformation/ARMCalc/ArmCalcService.svc/REST"


class ArmCalcClient(object):
    """
    Client for ArmCalc web service.
    """
    def __init__(self, url=DEFAULT_URL):
        self.url = url

    def batch(self, arm_calc_inputs):
        """Performs ArmCalc calculation on multiple input objects.

        Parameters
        ----------
        arm_calc_inputs: An iterator of ArmCalcInput objects.
        """
        if isinstance(arm_calc_inputs, ArmCalcInput):
            arm_calc_inputs = [arm_calc_inputs]
        ac_json = dumps(arm_calc_inputs, cls=ArmCalcJsonEncoder, skipkeys=True)
        url = "%s/CalcBatch" % self.url
        req = urllib2.Request(url, ac_json, headers={
            "Content-Type": "application/json"
        })
        try:
            response = urllib2.urlopen(req)
            output = response.read()
        except urllib2.HTTPError:
            sys.stderr.write(url)
            raise
        return output
