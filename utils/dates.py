from datetime import date, datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from log.logger import logging
from utils.decorator import timer

@timer
def human_duration(start:datetime, end:datetime) -> str:
    """"""
    attrs:list[str] = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']

    _readable = lambda delta: ['%d %s' % (getattr(delta, attr), attr if getattr(delta, attr) > 1 else attr[:-1]) for attr in attrs if getattr(delta, attr)]

    delta:relativedelta = relativedelta(end, start)
    l:list[str] = _readable(delta)
    return ' '.join(l)

@timer
def to_datetime(value:str, fmt:str = '%Y-%m') -> datetime:
    """Convert the date represented in value to a datetime using the format passed"""
    result:datetime = datetime.strptime(value, fmt)
    logging.debug('converting string to datetime', original=value, converted=result)

    return result
@timer
def to_date(value:str, fmt:str = '%Y-%m') -> date:
    """Convert the date represented in value to a date using the format passed"""
    return to_datetime(value, fmt).date()

@timer
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



@timer
def between(t:datetime, start_date:date, end_date:date) -> bool:
    """Confirms if datetime is between the date range and not None"""
    start:datetime = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=timezone.utc)
    end:datetime = datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0, tzinfo=timezone.utc)
    if t is not None:
        t = t.replace(tzinfo=timezone.utc)
    return (t is not None) and (t >= start and t <= end)

@timer
def year_month_list(start:date, end:date, fmt:str = '%Y-%m') -> list[str]:
    """Generate a list of YYYY-mm keys between the start and end date

    Will return the month of the end date as well.
    """
    return date_list( start=start, end=end, month=1 )

@timer
def date_list(start:date, end:date, year:int=0, month:int=0, day:int=0, format:str='%Y-%m') -> list[str]:
    """Generate a lsit of days in format between the start and end date passed.

    Allows chaging the interval dates are added by passing year / month / day params
    """
    items:list[str] = []

    e:date = end
    i:date = start

    # if we're using years, reset the months
    if year > 0:
        i = i.replace(month=1)
    # if we're using months, then reset the starting day so we capture the last month correctly
    elif month > 0:
        i = i.replace(day=1)

    while i <= e:
        items.append(i.strftime(format))
        i += relativedelta(years=year, months=month, days=day)

    items.sort()
    logging.debug("date list", start=start, end=end, result=items)
    return items
