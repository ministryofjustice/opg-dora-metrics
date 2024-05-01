from datetime import date, datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from log.logger import logging
from utils.decorator import timer

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
    d:list[str] = []

    e = end.replace(day=20)
    i = start.replace(day=1)
    while i <= e:
        d.append(i.strftime(fmt))
        i += relativedelta(months=1)
    d.sort()
    logging.debug("year month list", start=start, end=end, result=d)
    return d
