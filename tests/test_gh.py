import pytest
from github import Github
from github.Repository import Repository

from pprint import pp
from gh.workflows import workflow_total_duration


# creates real api calls, to is rate limited
@pytest.mark.parametrize("test_repo, test_workflow, expected_duration",
[
    # use a known workflow to find its duration
    ("ministryofjustice/opg-github-actions", 8434061820, 112),
    ("ministryofjustice/opg-dora-metrics", 8440646171, 133)
])
def test_workflow_total_duration(test_repo:str, test_workflow:int, expected_duration:int) :
    """Test that workflow total duration in seconds matches"""
    g:Github = Github()
    r:Repository = g.get_repo(test_repo)

    assert workflow_total_duration(r, test_workflow) == expected_duration
