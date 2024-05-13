from typing import TypeVar, Any
from collections.abc import MutableMapping

from log.logger import logging
from utils.decorator import timer

from pprint import pp
# source type
T = TypeVar('T', dict, MutableMapping)

@timer
def summed(grouped: dict[str, list[dict[str, Any]]], key:str) -> dict[str, dict[str,Any]]:
    """Generate a series of totals for the grouped information passed.

    Appends `_count` which is the counter of how many items found

    Example:
        `grouped = {'2024-01':[ {'avg':100, 'others':True}, {'avg':50} ]}`
        `key = 'avg'`
        returned:
            `{'2024-01': {'avg':150, '_count':2 } }`
    """
    summed:dict[str] = {}
    for k, items in grouped.items():
        if k not in summed:
            summed[k] = {key:0, '_count': 0}

        for i in items:
            summed[k][key] += i.get(key, 0)
            summed[k]['_count'] += 1
    return summed



@timer
def totals(grouped: dict[str, list[T]], total_vary_by:str = None) -> dict[str, dict[str,Any]]:
    """Generate a series of totals for the grouped information passed.

    Example:
        `grouped = {'2024-01':[ {'status':'y'}, {'status':'n'} ]}`
        `total_vary_by = 'status'`
        returned:
            `{'2024-01': {'total':2, 'total_y': 1, 'total_n':1 } }`
    """

    totals:dict[str] = {}

    for key, values in grouped.items():
        logging.debug('group key', key=key, type=type(key))
        if key not in totals:
            totals[key] = {}
        # overall total
        t:int = len(values)
        totals[key]['total'] = t
        logging.debug('overall total', key=key, total=t)
        # iterate over possible values of total_field if set
        if total_vary_by is not None:
            for v in values:
                field_value = v.get(total_vary_by)
                total_key = f'total_{field_value}'
                totals[key][total_key] = totals[key].get(total_key, 0 ) + 1
                logging.debug('count for each value of field', key=key, total_vary_by=total_vary_by, total_key=total_key)

    return totals
