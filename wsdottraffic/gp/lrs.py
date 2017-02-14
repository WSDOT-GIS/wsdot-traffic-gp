"""Linear referencing module
"""
from __future__ import unicode_literals, print_function

import re
import arcpy

_DEFAULT_ROUTE_ID_RE = re.compile(r"""^(
        (Begin)|(Start)
    )?(
        (R(oute)?ID)|(RoadName)
    )$""", re.IGNORECASE | re.VERBOSE)
_DEFAULT_FROM_RE = re.compile(r"""^(
        (Begin)|(Start)|(From)
    )?(
        (ARM)|(M(easure)?)
    )$""", re.IGNORECASE | re.VERBOSE)
_DEFAULT_TO_RE = re.compile(r"^(End)((ARM)|(M(easure)?))$",
                            re.IGNORECASE | re.VERBOSE)
_RE_TYPE = type(_DEFAULT_ROUTE_ID_RE)


def _get_table_fields(table):
    desc = arcpy.Describe(table)
    if not hasattr(desc, "fields"):
        raise TypeError("Table description has no 'fields' property.")
    else:
        return desc.fields  # pylint:disable=no-member


def _get_matching_field_name(table, field_re):
    if field_re is None:
        return field_re
    elif not isinstance(field_re, (str, _RE_TYPE)):
        raise TypeError(
            'The field_re paramter can only be str, regex, or None')
    elif isinstance(field_re, str):
        fields = _get_table_fields(table)
        output = None
        for field in fields:
            if re.fullmatch(field_re, field.name, re.IGNORECASE):
                output = field.name
                break
        if output is None:
            raise ValueError(
                'No field named "%s" could be found in table "%s"' % (
                    field_re, table
                ))
        return output
    else:
        output = None
        fields = _get_table_fields(table)
        for field in fields:
            if field_re.match(field.name):
                output = field.name
                break
        return output


def create_fc(route_layer,  # pylint: disable=too-many-arguments
              event_table,
              rl_route_field=_DEFAULT_ROUTE_ID_RE,
              ev_rid_field=_DEFAULT_ROUTE_ID_RE,
              ev_from_m=_DEFAULT_FROM_RE,
              ev_to_m=_DEFAULT_TO_RE):
    """Creates a feature class from event table.
    """
    # Make sure inputs exist.
    if not arcpy.Exists(route_layer):
        raise OSError(route_layer)
    elif not arcpy.Exists(event_table):
        raise OSError(event_table)
    elif rl_route_field is None or ev_rid_field is None or ev_from_m is None:
        raise TypeError(
            "Parameters for required fields cannot be None. (%s, %s, %s)" %
            (rl_route_field, ev_rid_field, ev_from_m))

    # Find route ID field for route fc
    rl_route_field = _get_matching_field_name(route_layer, rl_route_field)
    ev_rid_field = _get_matching_field_name(event_table, ev_rid_field)
    ev_from_m = _get_matching_field_name(event_table, ev_from_m)
    # End measure is not required
    if ev_to_m is not None:
        ev_to_m = _get_matching_field_name(event_table, ev_to_m)
        arcpy.AddError(
            "Could not determine end measure field automatically.")


def main():
    """called when run as a script."""
    create_fc("layers/WAPR.lyr",
              "TravelerInfo.gdb/HighwayAlerts")

if __name__ == '__main__':
    main()
