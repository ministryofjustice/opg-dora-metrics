from itertools import groupby
from typing import Callable, Any, TypeVar
from pprint import pp
from utils.decorator import timer
from log.logger import logging

T = TypeVar('T')
D = TypeVar('D')

@timer
def group(listing:list[T], group_function:Callable[[T], Any]) -> dict[str, list[T]]:
    """Generic grouping of lists that presumes the group_function handles the method for joining"""
    result:dict[str, list[T]] = {}
    logging.debug('grouping list together based on func', func=group_function)
    for key, values in groupby(listing, group_function):
        logging.debug('group key', key=key, type=type(key))
        if key not in result:
            result[key] = []
        result[key].extend(values)

    return result


@timer
def range_fill(items:dict[str, list[T]], keys:list[D]) -> dict[str, list[T]]:
    """Add a blank dict for any missing values in keys """
    for key in keys:
        if key not in items.keys():
            items[key] = {}
    return items
