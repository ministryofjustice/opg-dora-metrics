import os
import pytest
from datetime import date
from github import Github
from github.Repository import Repository
from gh.workflows import workflow_total_duration, workflow_runs, workflow_runs_by_name, workflow_runs_by_name_fuzzy
from gh.frequency import workflow_runs_by_month_fuzzy,working_days_in_month
from gh.auth import init
from gh.team import repositories_and_workflows
from gh.merges import merges_to_branch

from pprint import pp


@pytest.mark.parametrize("year, month, expected",
[
    ("2023", "02", 20),
    ("2023", "12", 21),
    ("2024", "01", 23),
    ("2024", "02", 21),
])
def test_working_days_in_month(year:str, month:str, expected:int):
    assert working_days_in_month(year, month) == expected

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


# test number of workflow runs for regex match (eg path to live testing)
@pytest.mark.parametrize("test_repo, test_dates, workflow_name, status, expected_count",
[
    # ("ministryofjustice/opg-lpa", "2024-02-01..2024-03-01", " live","success", 15),
    ("ministryofjustice/serve-opg", "2024-02-01..2024-03-01", " live$", "success", 3),
])
def test_workflow_runs_by_name_fuzzy_and_status(test_repo:str, test_dates:str, workflow_name:str, status:str, expected_count:int):
    """Test number of successful workflow runs for specifc workflows (eg path to live testing)"""
    g:Github = Github()
    r:Repository = g.get_repo(test_repo)
    w = workflow_runs_by_name_fuzzy(workflow_name, r, test_dates, "main", status)
    assert len(w) == expected_count


@pytest.mark.parametrize("test_repo, pattern, start, end, key, success, failure",
[
    ("ministryofjustice/serve-opg", " live$", date(2024, 2, 1), date(2024, 3, 1), "2024-02", 3, 2 ),
])
def test_workflow_runs_by_month_fuzzy(test_repo:str, pattern:str, start:date, end:date, key:str, success:int, failure:int):
    """Check that we find correct number of success and failures for the month"""
    g:Github = Github()
    r:Repository = g.get_repo(test_repo)
    res:dict = workflow_runs_by_month_fuzzy(pattern, r, start, end)
    assert res[key]['success'] == success
    assert res[key]['failure'] == failure


@pytest.mark.parametrize("org, team, expected_count",
[
    ("ministryofjustice", "opg", 111),
])
@pytest.mark.skipif(os.environ.get("GH_TOKEN", 0) == 0, reason="Github token env var (GH_TOKEN) not present")
def test_team_repositories(org:str, team:str, expected_count:int):
    """Make sure we find the at least the expected number of repos"""
    token = os.environ.get("GH_TOKEN", 0)
    _, _, t = init(token, org, team)
    res = repositories_and_workflows(t)
    assert len(res) >= expected_count


@pytest.mark.parametrize("repo, start, end, branch, key, success, failure",
[
    ("ministryofjustice/serve-opg", date(2024, 1, 1), date(2024, 3, 1), "main", "2024-02", 5, 0),
])
def test_merges_to_branch(repo:str, start:date, end:date, branch:str, key:str, success:int, failure:int):
    """Test how many merges are found for this repo"""
    g:Github = Github()
    r:Repository = g.get_repo(repo)
    res = merges_to_branch(r, start, end, branch)
    assert res[key]['success'] == success
    assert res[key]['failure'] == failure
