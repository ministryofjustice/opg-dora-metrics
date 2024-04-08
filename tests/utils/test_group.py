import pytest
from typing import Any, Callable
from datetime import datetime
from utils.group import group
from faker import Faker



from pprint import pp




@pytest.mark.parametrize(
    "data, test_key, expected_count",
    [
        (
            [
                {'id': 1, 'type':'test', 'status': 'active'},
                {'id': 2, 'type':'test', 'status': 'inactive'},
                {'id': 3, 'type':'test', 'status': 'pending'},
                {'id': 4, 'type':'production', 'status': 'active'},
            ],
            'test',
            3,
        )
    ]
)
def test_utils_group_variable_list_types(data:list[str,Any], test_key:str, expected_count):
    """Test that grouping differing types of lists by a known column provides correct results"""
    res:dict[str, Any] = group(data, lambda x : x.get('type'))
    test = res.get(test_key, [])
    assert len(test) == expected_count

@pytest.mark.parametrize(
    "data, test_key, expected_count",
    [
        (
            [
                {
                    'date': datetime(year=2024, month=1, day=10, hour=13, minute=1, second=1),
                    'name': 'path to live',
                    'conclusion': 'success'
                },
                {
                    'date': datetime(year=2024, month=2, day=10, hour=1, minute=1, second=1),
                    'name': 'path to live',
                    'conclusion': 'failure'
                },
                {
                    'date': datetime(year=2024, month=2, day=29, hour=23, minute=1, second=1),
                    'name': 'path to live',
                    'conclusion': 'success'
                },
                {
                    'date': datetime(year=2024, month=3, day=1, hour=0, minute=0, second=1),
                    'name': 'path to live',
                    'conclusion': 'success'
                },
            ],
            '2024-02',
            2
        ),
    ]
)
def test_utils_group_formatted_value(data:list[str,Any], test_key:str, expected_count):
    """Test that grouping differing types of lists by a known column provides correct results"""
    res:dict[str, Any] = group(data, lambda x : x.get('date').strftime('%Y-%m') )
    test = res.get(test_key, [])
    assert len(test) == expected_count
