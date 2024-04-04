from typing import TypeVar, Callable, Any

from log.logger import logging
from models.item import Item

from pprint import pp

# source type
T = TypeVar('T', Item, dict)


def averages(
        totals: dict[str, T],
        averaging_function:Callable[[str, Any], Any],
        prefix:str = 'total',
        merge:bool = True
        ) -> dict[str, Item]:
    """"""
    logging.debug('start')

    result:dict[str, Item] = {}

    for key, data in totals.items():
        logging.debug('averages for', key=key)
        avgs:dict[str, float] = {}

        for k, v in data.items():
            avg:float = averaging_function(key,  v)
            avgs[k.replace(prefix, 'average')] = avg

        logging.info('averages calculated', key=key, avg=avgs)

        if merge:
            logging.info('merging totals into average results', key=key)
            avgs.update(data)

        result[key] = Item(data=avgs)

    logging.debug('end')
    return result
