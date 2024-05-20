from datetime import datetime, date
import calendar

from dateutil.relativedelta import relativedelta
from pprint import pp

from app.log.logger import logging
from app.decorator import timer

def duration(start:datetime, end:datetime) -> str:
    """Return the human readable version of the duration between `start` and `end`"""
    logging.debug("Duration get", start=start, end=end)
    assert isinstance(start, datetime)
    assert isinstance(end, datetime)

    delta:relativedelta = relativedelta(end, start)
    date_properties:list[str] = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
    human:str = ""
    for attr in date_properties:
        value = getattr(delta, attr)
        if value > 1:
            human += f'{value} {attr} '
        elif value > 0:
            human += f'{value} {attr[:-1]} '
    # remove trailing space
    human = human.rstrip()
    logging.debug("Duration got", human=human, start=start, end=end)
    return human



def weekdays_in_month(period:date) -> int:
    """Find the number of weekdays (as a proxy measure for working days) for the month provided"""
    count:int = 0
    cal = calendar.Calendar()
    for week in cal.monthdayscalendar(period.year, period.month):
        for i, day in enumerate(week):
            if day == 0 or i >= 5:
                continue
            count += 1
    logging.debug('weekdays in month', month=period, count=count)
    return count
