"""Gets sheild type (US, SR (State Route), or IS (Interstate)) for routes
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re

ROUTE_RE = re.compile(r"""^(?P<shieldtype>
    (?P<us>US)|(?P<is>IS?)|(?P<sr>
        (?:SR)|(?:WA)
    )
)[\-\s](?P<route>\d+)$""", re.VERBOSE)

SHIELD_TYPE_US = "US"
SHIELD_TYPE_SR = "SR"
SHIELD_TYPE_IS = "I"

SHIELD_DICT = {
    2: SHIELD_TYPE_US,
    3: SHIELD_TYPE_SR,
    4: SHIELD_TYPE_SR,
    5: SHIELD_TYPE_IS,
    6: SHIELD_TYPE_SR,
    7: SHIELD_TYPE_SR,
    8: SHIELD_TYPE_SR,
    9: SHIELD_TYPE_SR,
    10: SHIELD_TYPE_SR,
    11: SHIELD_TYPE_SR,
    12: SHIELD_TYPE_US,
    14: SHIELD_TYPE_SR,
    16: SHIELD_TYPE_SR,
    17: SHIELD_TYPE_SR,
    18: SHIELD_TYPE_SR,
    19: SHIELD_TYPE_SR,
    20: SHIELD_TYPE_SR,
    21: SHIELD_TYPE_SR,
    22: SHIELD_TYPE_SR,
    23: SHIELD_TYPE_SR,
    24: SHIELD_TYPE_SR,
    25: SHIELD_TYPE_SR,
    26: SHIELD_TYPE_SR,
    27: SHIELD_TYPE_SR,
    28: SHIELD_TYPE_SR,
    31: SHIELD_TYPE_SR,
    41: SHIELD_TYPE_SR,
    82: SHIELD_TYPE_IS,
    90: SHIELD_TYPE_IS,
    92: SHIELD_TYPE_SR,
    96: SHIELD_TYPE_SR,
    97: SHIELD_TYPE_US,
    99: SHIELD_TYPE_SR,
    100: SHIELD_TYPE_SR,
    101: SHIELD_TYPE_US,
    102: SHIELD_TYPE_SR,
    103: SHIELD_TYPE_SR,
    104: SHIELD_TYPE_SR,
    105: SHIELD_TYPE_SR,
    106: SHIELD_TYPE_SR,
    107: SHIELD_TYPE_SR,
    108: SHIELD_TYPE_SR,
    109: SHIELD_TYPE_SR,
    110: SHIELD_TYPE_SR,
    112: SHIELD_TYPE_SR,
    113: SHIELD_TYPE_SR,
    115: SHIELD_TYPE_SR,
    116: SHIELD_TYPE_SR,
    117: SHIELD_TYPE_SR,
    119: SHIELD_TYPE_SR,
    121: SHIELD_TYPE_SR,
    122: SHIELD_TYPE_SR,
    123: SHIELD_TYPE_SR,
    124: SHIELD_TYPE_SR,
    125: SHIELD_TYPE_SR,
    127: SHIELD_TYPE_SR,
    128: SHIELD_TYPE_SR,
    129: SHIELD_TYPE_SR,
    131: SHIELD_TYPE_SR,
    141: SHIELD_TYPE_SR,
    142: SHIELD_TYPE_SR,
    150: SHIELD_TYPE_SR,
    153: SHIELD_TYPE_SR,
    155: SHIELD_TYPE_SR,
    160: SHIELD_TYPE_SR,
    161: SHIELD_TYPE_SR,
    162: SHIELD_TYPE_SR,
    163: SHIELD_TYPE_SR,
    164: SHIELD_TYPE_SR,
    165: SHIELD_TYPE_SR,
    166: SHIELD_TYPE_SR,
    167: SHIELD_TYPE_SR,
    169: SHIELD_TYPE_SR,
    170: SHIELD_TYPE_SR,
    171: SHIELD_TYPE_SR,
    172: SHIELD_TYPE_SR,
    173: SHIELD_TYPE_SR,
    174: SHIELD_TYPE_SR,
    181: SHIELD_TYPE_SR,
    182: SHIELD_TYPE_IS,
    193: SHIELD_TYPE_SR,
    194: SHIELD_TYPE_SR,
    195: SHIELD_TYPE_US,
    197: SHIELD_TYPE_US,
    202: SHIELD_TYPE_SR,
    203: SHIELD_TYPE_SR,
    204: SHIELD_TYPE_SR,
    205: SHIELD_TYPE_IS,
    206: SHIELD_TYPE_SR,
    207: SHIELD_TYPE_SR,
    211: SHIELD_TYPE_SR,
    213: SHIELD_TYPE_SR,
    215: SHIELD_TYPE_SR,
    221: SHIELD_TYPE_SR,
    223: SHIELD_TYPE_SR,
    224: SHIELD_TYPE_SR,
    225: SHIELD_TYPE_SR,
    231: SHIELD_TYPE_SR,
    240: SHIELD_TYPE_SR,
    241: SHIELD_TYPE_SR,
    243: SHIELD_TYPE_SR,
    260: SHIELD_TYPE_SR,
    261: SHIELD_TYPE_SR,
    262: SHIELD_TYPE_SR,
    263: SHIELD_TYPE_SR,
    270: SHIELD_TYPE_SR,
    271: SHIELD_TYPE_SR,
    272: SHIELD_TYPE_SR,
    274: SHIELD_TYPE_SR,
    278: SHIELD_TYPE_SR,
    281: SHIELD_TYPE_SR,
    282: SHIELD_TYPE_SR,
    283: SHIELD_TYPE_SR,
    285: SHIELD_TYPE_SR,
    290: SHIELD_TYPE_SR,
    291: SHIELD_TYPE_SR,
    292: SHIELD_TYPE_SR,
    300: SHIELD_TYPE_SR,
    302: SHIELD_TYPE_SR,
    303: SHIELD_TYPE_SR,
    304: SHIELD_TYPE_SR,
    305: SHIELD_TYPE_SR,
    307: SHIELD_TYPE_SR,
    308: SHIELD_TYPE_SR,
    310: SHIELD_TYPE_SR,
    395: SHIELD_TYPE_US,
    397: SHIELD_TYPE_SR,
    401: SHIELD_TYPE_SR,
    405: SHIELD_TYPE_IS,
    409: SHIELD_TYPE_SR,
    410: SHIELD_TYPE_SR,
    411: SHIELD_TYPE_SR,
    432: SHIELD_TYPE_SR,
    433: SHIELD_TYPE_SR,
    500: SHIELD_TYPE_SR,
    501: SHIELD_TYPE_SR,
    502: SHIELD_TYPE_SR,
    503: SHIELD_TYPE_SR,
    504: SHIELD_TYPE_SR,
    505: SHIELD_TYPE_SR,
    506: SHIELD_TYPE_SR,
    507: SHIELD_TYPE_SR,
    508: SHIELD_TYPE_SR,
    509: SHIELD_TYPE_SR,
    510: SHIELD_TYPE_SR,
    512: SHIELD_TYPE_SR,
    513: SHIELD_TYPE_SR,
    515: SHIELD_TYPE_SR,
    516: SHIELD_TYPE_SR,
    518: SHIELD_TYPE_SR,
    519: SHIELD_TYPE_SR,
    520: SHIELD_TYPE_SR,
    522: SHIELD_TYPE_SR,
    523: SHIELD_TYPE_SR,
    524: SHIELD_TYPE_SR,
    525: SHIELD_TYPE_SR,
    526: SHIELD_TYPE_SR,
    527: SHIELD_TYPE_SR,
    528: SHIELD_TYPE_SR,
    529: SHIELD_TYPE_SR,
    530: SHIELD_TYPE_SR,
    531: SHIELD_TYPE_SR,
    532: SHIELD_TYPE_SR,
    534: SHIELD_TYPE_SR,
    536: SHIELD_TYPE_SR,
    538: SHIELD_TYPE_SR,
    539: SHIELD_TYPE_SR,
    542: SHIELD_TYPE_SR,
    543: SHIELD_TYPE_SR,
    544: SHIELD_TYPE_SR,
    546: SHIELD_TYPE_SR,
    547: SHIELD_TYPE_SR,
    548: SHIELD_TYPE_SR,
    599: SHIELD_TYPE_SR,
    702: SHIELD_TYPE_SR,
    704: SHIELD_TYPE_SR,
    705: SHIELD_TYPE_IS,
    706: SHIELD_TYPE_SR,
    730: SHIELD_TYPE_US,
    821: SHIELD_TYPE_SR,
    823: SHIELD_TYPE_SR,
    900: SHIELD_TYPE_SR,
    902: SHIELD_TYPE_SR,
    903: SHIELD_TYPE_SR,
    904: SHIELD_TYPE_SR,
    906: SHIELD_TYPE_SR,
    970: SHIELD_TYPE_SR,
    971: SHIELD_TYPE_SR
}

_FMT_DICT = {
    SHIELD_TYPE_IS: "%s-%%d" % SHIELD_TYPE_IS,
    SHIELD_TYPE_US: "%s %%d" % SHIELD_TYPE_US,
    SHIELD_TYPE_SR: "%s %%d" % SHIELD_TYPE_SR,
}


# def _left_pad_to_3_digits(num: str or int) -> str:
def _left_pad_to_3_digits(num):
    return "{:0>3}".format(num)


# def label_to_3_digit_id(label: str or int) -> str:
def label_to_3_digit_id(label):
    """Converts a label with a route type prefix to
    three-digit route ID.
    """
    if isinstance(label, (int, float)) and label > 0 and label < 1000:
        return _left_pad_to_3_digits(label)

    match = ROUTE_RE.match(label)
    if match:
        match_dict = match.groupdict()
        route = int(match_dict["route"])
        # Return, padded with zeroes to three digits.
        return _left_pad_to_3_digits(route)
    elif re.match(r"^\d{1,3}", label):
        return _left_pad_to_3_digits(label)
    else:
        raise ValueError("Unexpected format: %s.", label)


# def id_to_label(sr_id: int or str) -> str:
def id_to_label(sr_id):
    """Converts a state route ID into a label.
    E.g., "005" -> "I-5"
    """
    if not isinstance(sr_id, (int, float)):
        sr_id = int(sr_id)
    shield = SHIELD_DICT[sr_id]
    return _FMT_DICT[shield] % sr_id
