from datetime import date, datetime, timezone
import calendar
from log.logger import logging


def str_to_date(value:str, fmt:str = '%Y-%m') -> date:
    """"""
    logging.debug('start')
    result:date = datetime.strptime(value, fmt).date()
    logging.debug('converting string to date', original=value, converted=result)
    logging.debug('end')

    return result

def weekdays_in_month(period:date) -> int:
    """"""
    logging.debug('start')
    logging.info('getting count fo weekdays for month', month=period)
    count:int = 0
    cal = calendar.Calendar()
    for week in cal.monthdayscalendar(period.year, period.month):
        for i, day in enumerate(week):
            if day == 0 or i >= 5:
                continue
            count += 1
    logging.info('getting count fo weekdays for month', month=period, count=count)
    logging.debug('end')
    return count




# def between(t:date, start_date:date, end_date:date) -> bool:
#     start:datetime = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=timezone.utc)
#     end:datetime = datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0, tzinfo=timezone.utc)
#     return (t is not None) and (t >= start and t <= end)

# def year_month_list(start:date, end:date) -> list[str]:
#     """Generate a list of YYYY-mm keys between the start and end date"""
#     d:list[str] = []
#     logging.debug(f"Generating year_month_range between [{start}] and [{end}]")
#     for y in range (start.year, end.year+1):
#         for m in range (start.month, end.month):
#             d.append(f'{y}-{m :02d}')
#     return d


# def weekdays_in_month(year:int, month:int) -> int:
#     """Rough calculation for week days within a month. This does not account for bank holidays."""
#     weekday_count:int = 0
#     cal = calendar.Calendar()
#     for week in cal.monthdayscalendar(year, month):
#         for i, day in enumerate(week):
#             # not this month's day or a weekend
#             if day == 0 or i >= 5:
#                 continue
#             weekday_count += 1
#     logging.debug(f"[{year}-[{month}] has [{weekday_count}] weekdays")
#     return weekday_count
