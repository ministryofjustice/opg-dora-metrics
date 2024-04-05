import pytest

from github.Repository import Repository
from github.WorkflowRun import WorkflowRun
from github.PullRequest import PullRequest

from models.keep import specs, spec, attrs
from pprint import pp


def test_models_keep():
    """Test the enum handling returns correct number"""
    assert len(specs(Repository)) == 2
    assert len(specs(WorkflowRun)) == 4
    assert len(specs(PullRequest)) == 4
    # make sure we get spec details back correctly
    assert spec(Repository, 'id') == {'attr': 'id', 'value_type': int, 'choices': None}
    # make sure the string values match
    assert attrs(Repository) == ['id', 'full_name']
