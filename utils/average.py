from typing import TypeVar, Callable, Any
from collections.abc import MutableMapping

from log.logger import logging
from utils.decorator import timer

from pprint import pp

# source type
T = TypeVar('T', dict, MutableMapping)

@timer
def avg(totals: dict[str, dict[str,float]], total_key:str, counter_key:str) -> dict[str, dict[str,Any]]:
    """Takes a series of total and counters an works out average
    """
    avgs:dict[str, dict[str,float]] = {}
    for k, item in totals.items():
        total:float = item.get(total_key)
        counter:int = item.get(counter_key)
        avgs[k] = {'total': total, 'count': counter, 'average': (total/counter) }
    return avgs

@timer
def averages(
        totals: dict[str, T],
        averaging_function:Callable[[str, Any], Any],
        prefix:str = 'total',
        merge:bool = True
        ) -> dict[str, dict[str,Any]]:
    """Takes a dict containing total data and works out the averages using the function passed in"""

    result:dict[str, dict] = {}

    for key, data in totals.items():
        logging.debug('averages for', key=key)
        avgs:dict[str, float] = {}

        for k, v in data.items():
            if prefix in k:
                avg:float = averaging_function(key,  v)
                avgs[k.replace(prefix, 'average')] = avg


        logging.debug('averages calculated', key=key, avg=avgs)

        if merge:
            logging.debug('merging totals into average results', key=key)
            avgs.update(data.items())

        result[key] = avgs

    return result
