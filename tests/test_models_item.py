import pytest
from typing import Any
from github.WorkflowRun import WorkflowRun

from models.item import Item

from pprint import pp


class Tester:
    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            self.__setattr__(k, v)

@pytest.mark.parametrize(
    "data, properties, test, expected",
    [
        (Tester(category='fiction', price=1.00, stock=5), None, 'price', 1.00),
        (WorkflowRun(requester=None, headers={}, attributes={'name': "test-workflow"}, completed=True), ['name', 'headers'], 'name', 'test-workflow'),
        ({'category': 'fiction', 'price':1.00, 'stock':5}, None, 'price', 1.00),
    ]
)
def test_models_Item_init(data:Any, properties:list[str]|None, test:str, expected:Any):
    """Ensure the init works from various sources and we can fetch a value correctly"""
    item = Item(data, properties)
    assert item.get(test) == expected


def test_models_Item_getters_setters():
    """Check getters and setters of the item are updated correctly"""
    data = Tester(category='fiction', price=1.00, stock=5, publisher={'name':'tester'})
    item = Item(data, None)
    # check getters
    assert item.category == item.get('category') == 'fiction'
    assert item.not_real == item.get('not_real') == None
    assert item.headers == item.get('headers') == None
    # check setters
    item.test_attr = 'new-string'
    assert item.test_attr == item.get('test_attr') == 'new-string'
    item.test_attr = 'new-string2'
    assert item.test_attr == item.get('test_attr') == 'new-string2'
    # check deletes
    del item.test_attr
    assert item.test_attr == item.get('test_attr') == None
    # check renames
    item.rename('stock', 'quantity')
    assert item.stock == item.get('stock') == None
    assert item.quantity == item.get('quantity') == 5
    item.quantity = 3
    assert item.quantity == item.get('quantity') == 3
    item.rename('quantity', 'stock')
    assert item.stock == item.get('stock') == 3
    assert item.quantity == item.get('quantity') == None
    # check types
    assert type(item.category) == type(item.get('category')) == str
    assert type(item.publisher) == type(item.get('publisher')) == dict
    assert type(item.price) == type(item.get('price')) == float
