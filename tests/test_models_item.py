import pytest
from datetime import datetime, date
from typing import Any
from faker import Faker

from github.WorkflowRun import WorkflowRun

from models.item import Item

from pprint import pp

fake = Faker()


class Tester:
    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            self.__setattr__(k, v)

@pytest.mark.parametrize(
    "data, properties, test, expected",
    [
        (Tester(category='fiction', price=1.00, stock=5), [], 'price', 1.00),
        (WorkflowRun(requester=None, headers={}, attributes={'name': "test-workflow"}, completed=True), ['name', 'headers'], 'name', 'test-workflow'),
        ({'category': 'fiction', 'price':1.00, 'stock':5}, [], 'price', 1.00),
    ]
)
def test_models_Item_init(data:Any, properties:list[str]|None, test:str, expected:Any):
    """Ensure the init works from various sources and we can fetch a value correctly"""
    item = Item(data, properties)
    assert item.get(test) == expected


def test_models_Item_getters_setters():
    """Check getters and setters of the item are updated correctly"""
    data = Tester(category='fiction', price=1.00, stock=5, publisher={'name':'tester'})
    item = Item(data, [])
    # check getters
    assert item.category == item.get('category') == 'fiction'
    assert item.get('not_real') == None
    assert item.get('headers') == None
    # check setters
    item.test_attr = 'new-string'
    assert item.test_attr == item.get('test_attr') == 'new-string'
    item.test_attr = 'new-string2'
    assert item.test_attr == item.get('test_attr') == 'new-string2'
    # check deletes
    del item.test_attr
    assert item.get('test_attr') == None
    # check renames!
    item.rename('stock', 'quantity')
    assert item.get('stock') == None
    assert item.quantity == item.get('quantity') == 5
    item.quantity = 3
    assert item.quantity == item.get('quantity') == 3
    item.rename('quantity', 'stock')
    assert item.stock == item.get('stock') == 3
    assert item.get('quantity') == None
    # check types
    assert item._type == type(data)
    assert type(item.category) == type(item.get('category')) == str
    assert type(item.publisher) == type(item.get('publisher')) == dict
    assert type(item.price) == type(item.get('price')) == float



@pytest.fixture
def fixture_workflow_runs():
    """Create is used to generate a list of WorkflowRun with count entries"""
    def create(count:int) -> list[WorkflowRun]:
        runs: list[WorkflowRun] = []

        for i in range(count):
            dt:datetime = fake.date_between(start_date="-2y", end_date="-1m")
            props = {
                'id': fake.random_number(),
                'created_at': dt.isoformat(),
                'name': fake.sentence(nb_words=4),
                'conclusion': 'success'
            }
            runs.append(
                WorkflowRun(requester=None, headers={}, attributes=props, completed=True)
            )
        return runs
    return create

def test_models_Item_rename_check(fixture_workflow_runs):
    """Generate a list of 10 WorkflowRun objects, convert them and then make sure the renaming of a field works"""
    for run in fixture_workflow_runs(10):
        item = Item(data=run)
        orig = item.get('created_at')
        item.rename('created_at', 'date')
        assert item.get('date') == orig
        assert item.get('created_at') == None
