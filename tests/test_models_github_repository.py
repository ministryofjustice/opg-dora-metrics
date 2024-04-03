import pytest
import os
from datetime import date, datetime
from github import Github
from github.PullRequest import PullRequest

from models.github_repository import GithubRepository
from models.simple import Simple

from pprint import pp


@pytest.mark.parametrize("slug, runs, start, end, total, success",
[
    ("ministryofjustice/serve-opg",
     [
         Simple(name="1", conclusion='failure', created_at=datetime(year=2024, month=1, day=10, hour=13, minute=1, second=1)),
         Simple(name="2", conclusion='success', created_at=datetime(year=2024, month=1, day=10, hour=13, minute=30, second=1)),
         Simple(name="3", conclusion='success', created_at=datetime(year=2024, month=2, day=18, hour=13, minute=30, second=1)),
         Simple(name="4", conclusion='success', created_at=datetime(year=2024, month=2, day=29, hour=13, minute=30, second=1)),
         Simple(name="excluded-by-date", conclusion='success', created_at=datetime(year=2024, month=3, day=2, hour=13, minute=30, second=1)),
     ],
     date(year=2024, month=1, day=1),
     date(year=2024, month=3, day=1),
     4,
     3),
])
def test_models_GithubRepository_aggregated_workflow_runs_success(
    slug:str, runs:list[Simple], start:date, end:date, total:int, success:int):
    """Check that aggregated workflow groups and creates totals correctly"""
    g:Github = Github()
    repo = GithubRepository(g, slug)
    agg = repo.aggregated_workflow_runs(runs, start, end)

    t: int = 0
    s: int = 0
    for ym, data in agg.items():
        t = t + data.total
        s = s + data.get('total_success')

    assert t == total
    assert s == success


# ################################################
# # REQUIRE GITHUB API CALLS TO BE MADE
# # Will be skipped if GH_TOKEN env var is not set
# ################################################
@pytest.mark.parametrize("slug",
[
    ("ministryofjustice/serve-opg")
])
@pytest.mark.skipif(os.environ.get("GH_TOKEN", 0) == 0, reason="Requires real api calls, Github token env var (GH_TOKEN) not present")
def test_models_GithubRepository_init_success(slug:str):
    """Test that the class inits and the slugs / names all match"""
    g:Github = Github()
    repo = GithubRepository(g, slug)
    assert repo.r.full_name == slug
    assert repo.name() == slug


@pytest.mark.parametrize("slug, workflow, start, end, total, success",
[
    ("ministryofjustice/serve-opg", " live", date(year=2024, month=2, day=1), date(year=2024, month=3, day=1), 5, 3),
])
@pytest.mark.skipif(os.environ.get("GH_TOKEN", 0) == 0, reason="Requires real api calls, Github token env var (GH_TOKEN) not present")
def test_models_GithubRepository_workflow_runs_success(slug:str, workflow:str, start:date, end:date, total:int, success:int):
    """Test the simple workflow runs are return in a matching way"""
    g:Github = Github()
    repo = GithubRepository(g, slug)
    runs = repo.workflow_runs(workflow, 'main', start, end)
    # get just the good ones
    good = [d for d in runs if d.get('conclusion') == 'success']
    assert len(runs) == total
    assert len(good) == success

@pytest.mark.parametrize("slug, branch, expected",
[
    ("ministryofjustice/serve-opg", "main", 128)
])
@pytest.mark.skipif(os.environ.get("GH_TOKEN", 0) == 0, reason="Requires real api calls, Github token env var (GH_TOKEN) not present")
def test_models_GithubRepository_pull_requests(slug:str, branch:str, expected:int):
    """Test that the class inits and the slugs / names all match"""
    g:Github = Github()
    repo = GithubRepository(g, slug)
    total, res = repo.pull_requests(branch)
    first = res[0]

    assert total == expected
    assert len(res) == expected
    assert isinstance(first.get('_type'), PullRequest) == True
