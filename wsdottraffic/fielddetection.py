"""A module for extracting information from lists of dicts for creating
geodatabase fields.
"""


from __future__ import (
    absolute_import, print_function, unicode_literals, division)

import re
from datetime import date, time, datetime

FIELD_TYPE_TEXT = "TEXT"
FIELD_TYPE_FLOAT = "FLOAT"
FIELD_TYPE_DOUBLE = "DOUBLE"
FIELD_TYPE_SHORT = "SHORT"
FIELD_TYPE_LONG = "LONG"
FIELD_TYPE_DATE = "DATE"
FIELD_TYPE_BLOB = "BLOB"
FIELD_TYPE_RASTER = "RASTER"
FIELD_TYPE_GUID = "GUID"

# Defines a ranking of field types.
_TYPE_RANKS = {
    FIELD_TYPE_GUID: 6,
    FIELD_TYPE_DATE: 6,
    FIELD_TYPE_RASTER: 6,

    FIELD_TYPE_BLOB: 5,

    FIELD_TYPE_DOUBLE: 4,
    FIELD_TYPE_FLOAT: 3,

    FIELD_TYPE_LONG: 2,
    FIELD_TYPE_SHORT: 1,

    FIELD_TYPE_TEXT: 0,
    None: -1
}


def _compare_types(name1, name2):
    """Compares two field type names.
    Returns an integer:
        1  if name1 should be used
        -1 if name2 should be used
        0 if the two names are the same
    Raises a ValueError if name1 and name2 are different but have the same
    rank.
    """
    if name1 == name2:
        return 0
    elif _TYPE_RANKS[name1] == _TYPE_RANKS[name2]:
        raise ValueError("Incompatible types: %s & %s" % (name1, name2))
    elif name1 is None:
        return -1
    elif name2 is None:
        return 1
    elif _TYPE_RANKS[name1] > _TYPE_RANKS[name2]:
        return 1
    else:
        return -1


def _get_field_type(value):
    """Determines a field type based on a value's type.
    """
    if value is None:
        return None
    field_type = None
    if isinstance(value, float):
        field_type = FIELD_TYPE_DOUBLE
    elif isinstance(value, int):
        field_type = FIELD_TYPE_LONG
    elif isinstance(value, (date, time, datetime)):
        field_type = FIELD_TYPE_DATE
    elif isinstance(value, str):
        guid_re = re.compile(r"^\{[a-f\d]+\}$", re.IGNORECASE)
        if guid_re.match(value):
            field_type = FIELD_TYPE_GUID
        else:
            field_type = FIELD_TYPE_TEXT
    return field_type


class FieldInfo(object):
    """Represents parameters for creating fields.

    Attributes:
        field_name: name of the field
        field_length: length of field. Only applicable to certain data types.
        field_type: data type of field
        field_is_nullable: indicates if the field is nullable.
    """
    def __init__(self, name, value, template=None):
        """Creates a new FieldInfo instance.

        Args:
            name: field name
            value: value used to determine the data type of the field
            template: Another FieldInfo object to be used as a template
        """
        self.field_name = None
        self.field_length = None
        self.field_type = None
        self.field_is_nullable = None
        if template and isinstance(template, FieldInfo):
            self.field_name = template.field_name

            # Get the field type of value
            new_field_type = _get_field_type(value)
            if template.field_type is None:
                self.field_type = new_field_type
            elif template.field_type == new_field_type:
                self.field_type = new_field_type
            else:
                # Make sure type is floating point
                compare_result = _compare_types(
                    new_field_type, template.field_type)
                if compare_result < 0:
                    self.field_type = template.field_type
                elif compare_result > 0:
                    self.field_type = new_field_type

            self.field_is_nullable = (
                template.field_is_nullable or value is None)
            if isinstance(value, str):
                new_len = len(value)
                if (
                        template.field_length is None or
                        template.field_length < new_len
                ):
                    self.field_length = new_len
                else:
                    self.field_length = template.field_length
            elif template.field_length is not None:
                self.field_length = template.field_length

        else:
            self.field_name = name
            self.field_type = _get_field_type(value)
            self.field_is_nullable = False
            self.field_length = None

            if self.field_type is None:
                self.field_is_nullable = True
            elif self.field_type == FIELD_TYPE_TEXT:
                self.field_length = len(value)

    @staticmethod
    def from_features(features):
        """Extracts a list of FieldInfos from a list of dicts representing
        GDB features

        Args:
            features: a list of dicts that define features
        Returns:
            A dict of field infos keyed by field_name.
        """
        master = {}
        for feature in features:
            for field_key, field_info in _iter_field_infos(feature):
                new_fi = FieldInfo(
                    field_key,
                    None,
                    field_info
                )
                master[field_key] = new_fi
        return master


def _iter_field_infos(feature_dict):
    """Iterates over dict key/value pairs and yields FieldInfo objects
    """
    for key, val in feature_dict.items():
        next_fi = FieldInfo(key, val)
        yield key, next_fi
