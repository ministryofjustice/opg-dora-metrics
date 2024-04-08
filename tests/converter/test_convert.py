import pytest

from tests.factory import faux

from github.Repository import Repository
from github.WorkflowRun import WorkflowRun
from github.PullRequest import PullRequest

from converter.convert import to, remapper
from pprint import pp

@pytest.mark.parametrize(
    "test_name",
    [
        ("ministryofjustice/serve-opg"),
        ("✓"),
        ("😀")
    ]
)
def test_converter_to_simple(test_name:str):
    """ensure the full_name property is set correctly."""

    res = to( faux.New(Repository, full_name=test_name) )
    assert res.get('full_name') == test_name


@pytest.mark.parametrize(
    "test_value, test_key, new_key",
    [("ministryofjustice/serve-opg", "full_name", "slug"),]
)
def test_converter_to_with_simple_remap(test_value:str, test_key:str, new_key:str):
    """ensure the full_name property swapped into the new name key."""

    args = {test_key:test_value}
    res = to( faux.New(Repository, **args), remap=[remapper(test_key, new_key)] )
    assert res.get(test_key) == None
    assert res.get(new_key) == test_value

@pytest.mark.parametrize(
    "test_value, test_key, new_key, remap_func",
    [("ministryofjustice/serve-opg", "full_name", "slug", lambda x: ('success')),]
)
def test_converter_to_with_simple_remap(test_value:str, test_key:str, new_key:str, remap_func):
    """ensure the full_name property changed key and value updated to the function result."""

    args = {test_key:test_value}
    res = to( faux.New(Repository, **args), remap=[remapper(test_key, new_key, remap_func)] )
    new_val = remap_func(test_value)
    assert res.get(test_key) == None
    assert res.get(new_key) != test_value
    assert res.get(new_key) == new_val
