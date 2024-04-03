import pytest
from typing import Any
from datetime import date, datetime

from models.aggregate import GroupBy, Totals
from models.simple import Simple

from pprint import pp


@pytest.mark.parametrize("simple_data, group_by, key, expected",
[
    (
        [
            {'name': "smith", 'age':16},
            {'name': "jones", 'age':40},
            {'name': "jones", 'age':30},
            {'name': "davies", 'age':20},
            {'name': "davies", 'age':21},
        ],
        'name',
        'jones',
        2
    ),
    (
        [
            {'name': "smith", 'age':16},
            {'name': "jones", 'age':40},
            {'name': "jones", 'age':30},
            {'name': "davies", 'age':20},
            {'name': "davies", 'age':21},
        ],
        'name',
        'smith',
        1
    ),
    (
        [
            {'name': "smith", 'age':16},
            {'name': "jones", 'age':40},
            {'name': "jones", 'age':30},
            {'name': "davies", 'age':20},
            {'name': "davies", 'age':21},
        ],
        'name',
        'not-real',
        0
    ),

])
def test_models_GroupBy_simple(simple_data:list[dict], group_by:str, key:str, expected:int ):
    """"""
    simples:list[Simple] = []
    for d in simple_data:
        simples.append(Simple(**d))
    grouped = GroupBy(group_by, simples)

    assert len(grouped.get(key, [])) == expected


@pytest.mark.parametrize("data, group_by, key, expected",
[
    (
        [
            {
                'created_at': datetime(year=2024, month=1, day=10, hour=13, minute=1, second=1),
                'name': 'path to live',
                'conclusion': 'success'
            },
            {
                'created_at': datetime(year=2024, month=2, day=10, hour=1, minute=1, second=1),
                'name': 'path to live',
                'conclusion': 'failure'
            },
            {
                'created_at': datetime(year=2024, month=2, day=10, hour=11, minute=1, second=1),
                'name': 'path to live',
                'conclusion': 'success'
            },
        ],
        'created_at',
        '2024-02',
        2
    ),

])
def test_models_GroupBy_custom_func(data:list[dict], group_by:str, key:str, expected:int ):
    """"""
    simples:list[Simple] = []
    gFunc = lambda x : x.get('created_at').strftime('%Y-%m')

    for d in data:
        simples.append(Simple(**d))
    grouped = GroupBy(group_by, simples, groupByFunc=gFunc)
    assert len(grouped.get(key, [])) == expected



@pytest.mark.parametrize("data, group_by, key, expected",
[
    (
        [
            {
                'created_at': datetime(year=2024, month=1, day=10, hour=13, minute=1, second=1),
                'name': 'path to live',
                'conclusion': 'success'
            },
            {
                'created_at': datetime(year=2024, month=2, day=10, hour=1, minute=1, second=1),
                'name': 'path to live',
                'conclusion': 'failure'
            },
            {
                'created_at': datetime(year=2024, month=2, day=10, hour=11, minute=1, second=1),
                'name': 'path to live',
                'conclusion': 'success'
            },
        ],
        'created_at',
        '2024-02',
        2
    ),

])
def test_models_Totals(data:list[dict], group_by:str, key:str, expected:int ):
    """"""
    simples:list[Simple] = []
    gFunc = lambda x : x.get('created_at').strftime('%Y-%m')

    for d in data:
        simples.append(Simple(**d))
    grouped = GroupBy(group_by, simples, groupByFunc=gFunc)
    totals = Totals('conclusion', grouped)

    assert totals.get(key).get('total') == expected
    assert totals.get(key).total == expected
