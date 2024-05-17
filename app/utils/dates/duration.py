from datetime import datetime, date

from dateutil.relativedelta import relativedelta
from pprint import pp

from app.log.logger import logging


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
