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
    """"""
    item = Item(data, properties)
    assert item.get(test) == expected
