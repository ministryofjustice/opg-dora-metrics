import pytest
import os
from datetime import date, datetime
from github import Github
from github.PullRequest import PullRequest

from models.github_repository import GithubRepository
from models.item import Item

from pprint import pp



# ################################################
# # REQUIRE GITHUB API CALLS TO BE MADE
# # Will be skipped if GITHUB_ACCESS_TOKEN env var is not set
# ################################################
@pytest.mark.parametrize("slug",
[
    ("ministryofjustice/serve-opg")
])
@pytest.mark.skipif(os.environ.get("GITHUB_ACCESS_TOKEN", 0) == 0, reason="Requires real api calls, Github token env var (GITHUB_ACCESS_TOKEN) not present")
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
@pytest.mark.skipif(os.environ.get("GITHUB_ACCESS_TOKEN", 0) == 0, reason="Requires real api calls, Github token env var (GITHUB_ACCESS_TOKEN) not present")
def test_models_GithubRepository_workflow_runs_success(slug:str, workflow:str, start:date, end:date, total:int, success:int):
    """Test the simple workflow runs are return in a matching way"""
    g:Github = Github()
    repo = GithubRepository(g, slug)
    runs = repo.workflow_runs(workflow, 'main', start, end)
    # get just the good ones
    good = [d for d in runs if d.get('conclusion') == 'success']
    assert len(runs) == total
    assert len(good) == success


@pytest.mark.parametrize("slug, branch, start, end, inrange",
[
    (
        "ministryofjustice/serve-opg",
        "main",
        date(year=2024, month=2, day=1),
        date(year=2024, month=3, day=1),
        5
    )
])
@pytest.mark.skipif(os.environ.get("GITHUB_ACCESS_TOKEN", 0) == 0, reason="Requires real api calls, Github token env var (GITHUB_ACCESS_TOKEN) not present")
def test_models_GithubRepository_pull_requests(slug:str, branch:str, start:date, end:date, inrange:int):
    """Test that the class inits and the slugs / names all match"""
    g:Github = Github()
    repo = GithubRepository(g, slug)
    all = repo.pull_requests(branch, start, end)
    first = all[0]
    pp(first)

    assert len(all) == inrange
    # assert isinstance(first._type, PullRequest) == True
