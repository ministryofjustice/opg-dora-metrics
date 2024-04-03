from itertools import groupby
from typing import Callable, Any
import logging

from models.simple import Simple

from pprint import pp

class GroupBy:
    """GroupBy will handle converting a list of Simple into a dict grouped by a field name"""

    def __new__(self,
            by:str,
            data:list[Simple],
            sortByFunc:Callable[[Simple], Any] = None,
            groupByFunc:Callable[[Simple], Any]= None,
        ) -> dict[str, list[Simple]]:
        """Take group by field and source list of data and convert into a dict.

        Keys of the dict are generated from the output of groupByFunc
        """
        if sortByFunc is None:
            sortByFunc = lambda x : x.get(by)
        if groupByFunc is None:
            groupByFunc = lambda x : x.get(by)

        ordered = sorted(data, key=sortByFunc)
        grouped:dict[str, list[Simple]] = {}
        for key, value in groupby(ordered, groupByFunc):
            if key not in grouped:
                grouped[key] = []
            grouped[key].extend(value)
        return grouped


class Totals:
    """Takes a dict with a list under each and generates total counters"""

    def __new__(self, by:str, grouped: dict[str, list[Simple]] ) -> dict[str, Simple]:
        """"""
        totals = {}

        for key, values in grouped.items():
            # default
            if key not in totals:
                totals[key] = {}
            # overall total
            totals[key]['total'] = len(values)
            # now iterate over all and update
            for v in values:
                # field value total
                field = v.get(by)
                sub:str = f'total_{field}'
                totals[key][sub] = totals[key].get(sub, 0) + 1

        # swap to Simple
        converted:dict[str, Simple] = {k: Simple(**d) for k, d in totals.items()}
        return converted
