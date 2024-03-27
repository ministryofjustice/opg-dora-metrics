import pytest
from github import Github
from github.Repository import Repository

from pprint import pp
from gh.workflows import workflow_total_duration, workflow_runs, workflow_runs_by_name, workflow_runs_by_name_fuzzy


###### THESE TESTS CALL REAL API END POINTS! ######

# test durations match known values
@pytest.mark.parametrize("test_repo, test_workflow, expected_duration",
[
    ("ministryofjustice/opg-github-actions", 8434061820, 112),
    ("ministryofjustice/opg-dora-metrics", 8440646171, 133)
])
def test_workflow_total_duration_matches(test_repo:str, test_workflow:int, expected_duration:int) :
    """Test that workflow total duration in seconds matches"""
    g:Github = Github()
    r:Repository = g.get_repo(test_repo)

    assert workflow_total_duration(r, test_workflow) == expected_duration

# test number of workflow runs matches known values
@pytest.mark.parametrize("test_repo, test_dates, expected_count",
[
    # ("ministryofjustice/opg-lpa", "2024-02-01..2024-03-01", 220),
    ("ministryofjustice/serve-opg", "2024-02-01..2024-03-01", 5),
])
def test_workflow_runs(test_repo:str, test_dates:str, expected_count:int):
    """Test number of workflow runs matches known values"""
    g:Github = Github()
    r:Repository = g.get_repo(test_repo)
    w = workflow_runs(r, test_dates, "main")
    assert len(w) == expected_count


# test number of workflow runs for specifc workflows (eg path to live testing)
@pytest.mark.parametrize("test_repo, test_dates, workflow_name, expected_count",
[
    # ("ministryofjustice/opg-lpa", "2024-02-01..2024-03-01", "[Workflow] Path to Live", 15),
    ("ministryofjustice/serve-opg", "2024-02-01..2024-03-01", "Path to Live", 5),
])
def test_workflow_runs_by_name(test_repo:str, test_dates:str, workflow_name:str, expected_count:int):
    """Test number of workflow runs for specifc workflows (eg path to live testing)"""
    g:Github = Github()
    r:Repository = g.get_repo(test_repo)
    w = workflow_runs_by_name(workflow_name, r, test_dates, "main")
    assert len(w) == expected_count


# test number of workflow runs for regex match (eg path to live testing)
@pytest.mark.parametrize("test_repo, test_dates, workflow_name, expected_count",
[
    # ("ministryofjustice/opg-lpa", "2024-02-01..2024-03-01", " live", 15),
    ("ministryofjustice/serve-opg", "2024-02-01..2024-03-01", " live", 5),
])
def test_workflow_runs_by_name_fuzzy(test_repo:str, test_dates:str, workflow_name:str, expected_count:int):
    """Test number of workflow runs for specifc workflows (eg path to live testing)"""
    g:Github = Github()
    r:Repository = g.get_repo(test_repo)
    w = workflow_runs_by_name_fuzzy(workflow_name, r, test_dates, "main")
    assert len(w) == expected_count
