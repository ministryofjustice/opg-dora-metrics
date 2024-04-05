from datetime import date, datetime, timezone
import calendar
from log.logger import logging
from utils.decorator import timer

@timer
def str_to_date(value:str, fmt:str = '%Y-%m') -> date:
    """Convert the date represented in value to a date using the format and timezone passed"""
    result:date = datetime.strptime(value, fmt).date()
    logging.debug('converting string to date', original=value, converted=result)

    return result

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
    logging.info('getting count fo weekdays for month', month=period, count=count)
    return count



@timer
def between(t:datetime, start_date:date, end_date:date) -> bool:
    t = t.replace(tzinfo=timezone.utc)
    start:datetime = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=timezone.utc)
    end:datetime = datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0, tzinfo=timezone.utc)
    return (t is not None) and (t >= start and t <= end)

# def year_month_list(start:date, end:date) -> list[str]:
#     """Generate a list of YYYY-mm keys between the start and end date"""
#     d:list[str] = []
#     logging.debug(f"Generating year_month_range between [{start}] and [{end}]")
#     for y in range (start.year, end.year+1):
#         for m in range (start.month, end.month):
#             d.append(f'{y}-{m :02d}')
#     return d
