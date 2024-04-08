import pytest
from datetime import datetime, date
from utils.dates import year_month_list
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
