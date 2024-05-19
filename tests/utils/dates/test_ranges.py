import pytest
from datetime import datetime, date
from pprint import pp

from app.dates.ranges import date_range, Increment, date_range_as_strings
from app.dates.convert import to_date

################################################
# Tests
################################################

@pytest.mark.parametrize(
    "lower, upper, format, interval, expected",
    [
        #years
        ("2023", "2024", '%Y', Increment.YEAR, 2),
        ("2024", "2050", '%Y',Increment.YEAR, 27),

        # months
        ("2023-10", "2023-12",'%Y-%m', Increment.MONTH, 3),
        ("2022-02", "2023-02",'%Y-%m', Increment.MONTH, 13),
        ("2022-02", "2023-04",'%Y-%m', Increment.MONTH, 15),
        # days
        ("2024-02-28", "2024-03-01",'%Y-%m-%d', Increment.DAY, 3),
        ("2024-02-28", "2025-03-01",'%Y-%m-%d', Increment.DAY, 368),
        ("2024-03-01", "2025-03-01",'%Y-%m-%d', Increment.DAY, 366),
    ]
)
def test_utils_ranges_date_range(lower:str, upper:str, format:str, interval:Increment, expected:int):
    """Test that """
    dates:list[date] = date_range(to_date(lower, format), to_date(upper, format), interval)
    strings:list[date] = date_range_as_strings(to_date(lower, format), to_date(upper, format), interval)

    assert expected == len(dates)
    assert expected == len(strings)
