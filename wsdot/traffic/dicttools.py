"""Functions for use with dicts
"""


def dict_has_all_keys(dct, *keys):
    """Determines if a dict contains all of the given keys.
    Returns True if all keys are contained in dict, False otherwise.
    """
    for key in keys:
        if key not in dct:
            return False
    return True
