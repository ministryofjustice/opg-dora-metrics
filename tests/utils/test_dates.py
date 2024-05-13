import pytest
from datetime import datetime, date
from utils.dates import year_month_list, date_list
from pprint import pp


@pytest.mark.parametrize(
        "start, end, expected",
        [
            (date(year=2023, month=1, day=1), date(year=2023, month=3, day=10), 3),
            (date(year=2023, month=2, day=1), date(year=2024, month=2, day=1), 13),
            (date(year=2023, month=2, day=28), date(year=2024, month=4, day=1), 15),
        ]
)
def test_utils_dates_year_month_list(start:date, end:date, expected:int):
    res = year_month_list(start, end)
    assert len(res) == expected



@pytest.mark.parametrize(
        "start, end, y, m, d, f, count",
        [
            (date(year=2023, month=1, day=1), date(year=2023, month=3, day=10), 0, 1, 0, '%Y-%m', 3),
            (date(year=2023, month=2, day=1), date(year=2024, month=2, day=1), 0, 1, 0, '%Y-%m',13),
            (date(year=2023, month=2, day=28), date(year=2024, month=4, day=20), 0, 1, 0, '%Y-%m',15),

            (date(year=2023, month=2, day=28), date(year=2023, month=3, day=5), 0, 0, 1, '%Y-%m-%d',6),
            (date(year=2023, month=1, day=1), date(year=2024, month=1, day=1), 0, 0, 1, '%Y-%m-%d',366),
            # leap year days
            (date(year=2024, month=2, day=28), date(year=2024, month=3, day=1), 0, 0, 1, '%Y-%m-%d',3),
            # year check
            (date(year=2024, month=2, day=1), date(year=2050, month=3, day=27), 1, 0, 0, '%Y',27),
        ]
)
def test_utils_dates_date_list(start:date, end:date, y:int, m:int, d:int, f:str, count:int):
    res = date_list(start, end, year=y, month=m, day=d, format=f)
    assert len(res) == count
