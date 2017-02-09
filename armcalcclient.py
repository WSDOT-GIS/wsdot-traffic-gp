"""Client for calling ArmCalc web serivce
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sys import version_info


from datetime import datetime, date
from json import JSONEncoder, dumps, loads

from parseutils import to_wcf_date, parse_wcf_date

# Choose correct library for Python version
if version_info.major <= 2:
    from urllib2 import urlopen, HTTPError, Request
else:
    from urllib.request import urlopen, Request  # pylint: disable=no-name-in-module,import-error
    from urllib.error import HTTPError  # pylint: disable=no-name-in-module,import-error

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

    def __repr__(self):
        return 'ArmCalcInput(CalcType=%s, SR=%s, RRT=%s,\
RRQ=%s, ABIndicator=%s, ReferenceDate=%s, ARM=%s, SRMP=%s, \
ResponseDate=%s, TransId=%s)' % (self.CalcType, self.SR, self.RRT, self.RRQ,
                                 self.ABIndicator, self.ReferenceDate,
                                 self.ARM, self.SRMP, self.ResponseDate,
                                 self.TransId)


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

    def __repr__(self):
        return 'ArmCalcOutput(CalcType=%s, SR=%s, RRT=%s,\
RRQ=%s, ABIndicator=%s, ReferenceDate=%s, ARM=%s, SRMP=%s, \
ResponseDate=%s, TransId=%s, CalculationReturnCode=%s, \
CalculationReturnMessage=%s,RealignmentDate=%s)' % (
    self.CalcType, self.SR, self.RRT, self.RRQ, self.ABIndicator,
    self.ReferenceDate, self.ARM, self.SRMP, self.ResponseDate, self.TransId,
    self.CalculationReturnCode, self.CalculationReturnMessage,
    self.RealignmentDate)

DEFAULT_URL = \
    "http://webapps.wsdot.loc/StateRoute/LocationReferencingMethod/\
Transformation/ARMCalc/ArmCalcService.svc/REST"


def _hook(val):
    if isinstance(val, str):
        if len(val) == 0:
            return None
        return parse_wcf_date(val)
    return val


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
        ac_json = dumps(arm_calc_inputs, cls=ArmCalcJsonEncoder, skipkeys=True,
                        ensure_ascii=True)
        ac_json = bytearray(ac_json, 'utf-8')
        url = "%s/CalcBatch" % self.url
        headers = {
            "Content-Type": "application/json"
        }
        try:
            req = Request(url, data=ac_json, headers=headers)
            response = urlopen(req)
            out_json = response.read()
        except HTTPError:
            raise
        if version_info.major <= 2:
            out_dict_list = loads(str(out_json),
                                  object_hook=_hook)
        else:
            out_dict_list = loads(str(out_json, encoding="utf-8"),
                                  object_hook=_hook)
        out_list = []
        for item in out_dict_list:
            out_list.append(ArmCalcOutput(**item))
        return out_list
