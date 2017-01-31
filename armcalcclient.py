"""Client for calling ArmCalc web serivce
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# pylint: disable=invalid-name

CALC_TYPE_SRMP_TO_ARM = 0
CALC_TYPE_ARM_TO_SRMP = 1


class ArmCalcInput(object):
    """ArmCalc input
    """
    def __init__(self, CalcType=CALC_TYPE_SRMP_TO_ARM, SR=None, RRT=None,
                 RRQ=None, ABIndicator=None, ReferenceDate=None, ARM=None,
                 SRMP=None, ResponseDate=None, TransId=None):
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


class ArmCalcOutput(ArmCalcInput):
    """ArmCalc output
    """
    def __init__(self, CalcType=CALC_TYPE_SRMP_TO_ARM, SR=None, RRT=None,
                 RRQ=None, ABIndicator=None, ReferenceDate=None, ARM=None,
                 SRMP=None, ResponseDate=None, TransId=None,
                 CalculationReturnCode=None, CalculationReturnMessage=None,
                 RealignmentDate=None):
        super(ArmCalcOutput, self).__init__(CalcType, SR, RRT, RRQ,
                                            ABIndicator,
                                            ReferenceDate, ARM, SRMP,
                                            ResponseDate, TransId)
        # Calculation return code.
        self.CalculationReturnCode = CalculationReturnCode
        # Calulation return message. Will not have value if return code is 0.
        self.CalculationReturnMessage = CalculationReturnMessage
        # Realignment date. Date that a route was last realigned.
        self.RealignmentDate = RealignmentDate
