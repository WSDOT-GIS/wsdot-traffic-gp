"""Functions for use with dicts
"""
from typing import Any, Iterator, Tuple, Sequence

def dict_has_all_keys(dct: dict, *keys: Sequence[str]) -> bool:
    """Determines if a dict contains all of the given keys.
    Returns True if all keys are contained in dict, False otherwise.
    """
    for key in keys:
        if key not in dct:
            return False
    return True

def flatten_dict(dct: dict, parent_key: str = None) -> Iterator[Tuple[str, Any]]:
    """Generator function that flattens out nested dictionaries

    Args:
        dct: a dict object
        parent_key: this is only used for recursive calls. When a dict contains another dict,
            the key of that dict value will be used here.

    Yields:
        A tuple: key (str) and a value (non-dict value)
    """
    for key, val in dct.items():
        if isinstance(val, dict):
            if parent_key is not None:
                yield from flatten_dict(val, parent_key + key)
            else:
                yield from flatten_dict(val, key)
        else:
            if parent_key is not None:
                yield parent_key + key, val
            else:
                yield key, val
