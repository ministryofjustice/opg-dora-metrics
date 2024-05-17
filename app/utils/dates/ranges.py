from datetime import date, datetime
from enum import Enum
from dateutil.relativedelta import relativedelta
from pprint import pp
from app.decorator import timer

# how we increment data ranges
__increments__: dict = {
    'YEAR':{'increment': 'years', 'format': '%Y' },
    'MONTH':{'increment': 'months', 'format': '%Y-%m' },
    'DAY': {'increment': 'days', 'format': '%Y-%m-%d' },
}

class Increment(Enum):
    YEAR    = 'YEAR'
    MONTH   = 'MONTH'
    DAY     = 'DAY'

@timer
def date_range(start:date, end:date, inc:Increment = Increment.MONTH) -> list[date]:
    """Creates a list of dates from the start to end date"""
    items:list[str] = []
    e:date = end
    i:date = start
    # reset parts of the start date so when incrementing the values we
    # dont skip values that should be in range
    if inc == Increment.YEAR:
        i = i.replace(month=1)
    elif inc == Increment.MONTH:
        i = i.replace(day=1)
    
    key:str = __increments__[inc.value]['increment']
    by:dict = {key: 1}
    while i <= e:
        items.append(i)
        i += relativedelta(**by)
    items.sort()
    return items

@timer
def date_range_as_strings(start:date, end:date, inc:Increment = Increment.MONTH) -> list[str]:
    """Creates a list of strings from the start to end date"""
    date_items:list[date] = date_range(start=start, end=end, inc=inc)
    format:str = __increments__[inc.value]['format']    
    return [i.strftime(format) for i in date_items]
