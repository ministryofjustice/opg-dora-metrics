from typing import TypeVar

from log.logger import logging
from models.item import Item
from utils.decorator import timer
# source type
T = TypeVar('T', Item, dict)

@timer
def totals(grouped: dict[str, list[T]], total_vary_by:str = None) -> dict[str, Item]:
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
                logging.debug('count for each value of field', key=key, field=total_vary_by, variant=total_key)

    result:dict[str, Item] = {k: Item(values) for k, values in totals.items()}
    return result
