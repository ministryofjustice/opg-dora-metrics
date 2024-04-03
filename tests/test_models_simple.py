import pytest
from typing import Any
from github.WorkflowRun import WorkflowRun

from models.simple import Simple


class TestSimpleClass:
    """Test class used to check conversion from another class"""
    name:str
    address:dict = {}

    def __init__(self, name:str, address:dict) -> None:
        self.name = name
        self.address = address

@pytest.mark.parametrize("simple_data, test_property, expected, expected_t",
[
    ({'name': "test", 'age':16}, 'name', 'test', str),
    ({'name': "test", 'age':16}, 'age', 16, int),
    ({'name': "test", 'address': {'line1':'test nested'}}, 'name', 'test', str),
    ({'name': "test", 'address': {'line1':'test nested'}}, 'address', {'line1':'test nested'}, dict),
])
def test_models_Simple_get_set_del(simple_data:dict, test_property:str, expected:Any, expected_t:Any):
    """Test the Simple class is created and properties are accessible, match values and their expected types"""
    s = Simple(**simple_data)
    assert s.get(test_property) == expected
    assert isinstance( s.get(test_property), expected_t) == True
    # now set it directly and re-test
    s.set(test_property, 'other')
    assert s.get(test_property) != expected
    assert s.get(test_property) == 'other'
    # test the delete
    # same as s.delete(test_property)
    del s[test_property]
    assert s.get(test_property) == None



@pytest.mark.parametrize("data, keys, test_property, expected, expected_t",
[
    (
        TestSimpleClass("test1", {'line1':'test address 1'}),
        ['name', 'address'],
        'name',
        'test1',
        str
    ),
    (
        TestSimpleClass("test2", {'line':'test address 2'}),
        ['name', 'address'],
        'address',
        {'line':'test address 2'},
        dict
    ),
    (
        WorkflowRun(requester=None, headers={}, attributes={'name': "test-workflow"}, completed=True),
        ['name'],
        'name',
        'test-workflow',
        str
    ),
    (
        {'name': "name-with-no-address", 'address': {}},
        ['name'],
        'address',
        None,
        type(None)
    ),
    (
        {'name': "test-name", 'address': {}},
        ['name', 'address'],
        'name',
        'test-name',
        str
    )
])
def test_models_Simple_instance_get_set(data, keys:list[str], test_property:str, expected:Any, expected_t:Any):
    """Test the Simple class is created correctly from the import and properties are accessible, match values and their expected types"""
    s:Simple = Simple.instance(data, keys)
    val = s.get(test_property)
    assert val == expected
    assert isinstance( s.get(test_property), expected_t) == True
