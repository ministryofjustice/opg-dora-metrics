import pytest
from typing import Any, Callable
from utils.average import averages
from utils.dates import weekdays_in_month, to_date

from pprint import pp


@pytest.mark.parametrize(
    "data, test_key, expected",
    [
        (
            {
                '2024-01': {'total': (23*2), 'total_y': (23*1.5), 'total_n':(23*0.5)},
                # 21 is working days in this month
                '2024-02': {'total': (21*4), 'total_y': (21*3), 'total_n': (21*1) },
            },
            '2024-02',
            4.0
        ),

    ]
)
def test_utils_averages(data:dict[str,dict], test_key:str, expected:int):
    """Test the average calculations work with lamnda"""
    # lambda to devide the value by the number of weekdays for the month
    f = lambda month, value: ( round( value / weekdays_in_month( to_date(month) ), 2 ) )

    res:dict[str, Any] = averages(data, f)
    test = res[test_key]
    assert test.get('average') == expected
