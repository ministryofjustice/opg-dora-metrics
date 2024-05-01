import pytest

from github.Repository import Repository
from github.WorkflowRun import WorkflowRun
from github.PullRequest import PullRequest

from converter.meta import properties, property, attributes, _PropertyTypes
from pprint import pp


def test_converter_meta():
    """Test the enum handling returns correct number"""
    assert len(properties(Repository)) == 2
    assert len(properties(Repository)) == 2
    assert len(properties(WorkflowRun)) == 4
    assert len(properties(PullRequest)) == 5

    # make sure we get spec details back correctly
    assert property(Repository, 'id') == {'attribute': 'id', 't': _PropertyTypes.INT}
    # make sure the string values match
    assert attributes(Repository) == ['id', 'full_name']
