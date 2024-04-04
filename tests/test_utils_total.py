import pytest
from typing import Any, Callable
from datetime import datetime
from models.item import Item
from utils.group import group
from utils.total import totals

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
                '2024-01': [Item(data={'status': 'y', 'name': 'one'})],
                '2024-02': [Item(data={'status': 'n', 'name': 'one'}), Item(data={'status': 'y', 'name': 'one'}), Item(data={'status': 'y', 'name': 'two'})],
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
