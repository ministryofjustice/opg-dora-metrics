from itertools import groupby
from typing import Callable, Any, TypeVar


from log.logger import logging

T = TypeVar('T')


def group(listing:list[T], group_function:Callable[[T], Any]) -> dict[str, list[T]]:
    """Generic grouping of lists that presumes the group_function handles the method for joining"""
    result:dict[str, list[T]] = {}
    logging.debug('start')
    logging.info('grouping list together')
    for key, values in groupby(listing, group_function):
        logging.debug('group key', key=key, type=type(key))
        if key not in result:
            result[key] = []
        result[key].extend(values)

    logging.debug('end')
    return result
