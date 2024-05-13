import pytest
from typing import Any, Callable
from datetime import datetime
from utils.total import totals, summed

from pprint import pp


@pytest.mark.parametrize(
    "data, test_key, expected",
    [
        (
            {
                '2024-01': [{'status': 'y', 'name': 'one'}],
                '2024-02': [{'status': 'n', 'name': 'one'}, {'status': 'y', 'name': 'one'}, {'status': 'y', 'name': 'two'}],
            },
            '2024-02',
            3
        ),
        (
            {
                '2024-01': [{'status': 'y', 'name': 'one'}],
                '2024-02': [{'status': 'n', 'name': 'one'}, {'status': 'y', 'name': 'one'}, {'status': 'y', 'name': 'two'}],
            },
            '2024-01',
            1
        ),
    ]
)
def test_utils_totals_from_group(data:dict[str,list[Any]], test_key:str, expected:int):
    """"""
    res:dict[str, Any] = totals(data, 'status')
    test = res[test_key]
    assert test.get('total') == expected


@pytest.mark.parametrize(
    "data, test_key, expected",
    [
        (
            {
                '2024-01': [{'avg': 99, 'name': 'one'}, {'avg': 100.0, 'name': 'one'}],
                '2024-02': [{'avg': 50, 'name': 'one'}, {'avg': 100, 'name': 'one'}],
            },
            '2024-02',
            150
        ),
        (
            {
                '2024-01': [{'avg': 99.8, 'name': 'one'}, {'avg': 100, 'name': 'one'}],
                '2024-02': [{'avg': 50, 'name': 'one'}, {'avg': 100, 'name': 'one'}],
                '2024-03': [{'avg': 100, 'name': 'one'}, {'avg': 100, 'name': 'one'}],
            },
            '2024-01',
            199.8
        ),
    ]
)
def test_utils_totals_summed(data:dict[str,list[Any]], test_key:str, expected:float):
    """"""
    res:dict[str, Any] = summed(data, 'avg')
    pp(res)
    assert res[test_key]['avg'] == expected
