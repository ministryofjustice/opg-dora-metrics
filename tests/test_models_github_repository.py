import pytest
import os
from datetime import date, datetime
from unittest.mock import patch

from faker import Faker

from github import Github
from github.PullRequest import PullRequest
from github.WorkflowRun import WorkflowRun
from github.Repository import Repository

from models.github_repository import GithubRepository
from models.item import Item


from pprint import pp

################################################
# Fixtures & side effects
################################################
fake = Faker()

@pytest.fixture
def fixture_repository():
    def create(**kwargs) -> Repository:
        return Repository(requester=None, headers={}, attributes=kwargs, completed=True)
    return create

@pytest.fixture
def fixture_workflow_run():
    def create(**kwargs) -> WorkflowRun:
        return WorkflowRun(requester=None, headers={}, attributes=kwargs, completed=True)
    return create

@pytest.fixture
def fixture_workflow_runs_fixed_failures():
    # args[0] is count of how many to create
    def create(total:int, success:int, start:date, end:date) -> list[WorkflowRun]:
        runs: list[WorkflowRun] = []

        for i in range(total):
            dt:datetime = fake.date_between(start_date=start, end_date=end)
            props = {
                'created_at': dt.isoformat(),
                'name': fake.sentence(nb_words=4),
                'conclusion': 'success' if i < success else 'failure'
            }
            runs.append(
                WorkflowRun(requester=None, headers={}, attributes=props, completed=True)
            )

        return runs
    return create


################################################
# Tests
################################################
@pytest.mark.parametrize("slug",
[
    ("ministryofjustice/serve-opg")
])
def test_models_GithubRepository_init_success(slug:str, fixture_repository):
    """Test that the class inits and the slugs / names all match"""

    with patch('models.github_repository.GithubRepository._repo') as repo_mock:
        repo_mock.return_value = fixture_repository(full_name=slug)

    g:Github = Github()
    repo = GithubRepository(g, slug)
    assert repo.r.full_name == slug
    assert repo.name() == slug


@pytest.mark.parametrize("slug, workflow, start, end, total, success",
[
    ("ministryofjustice/serve-opg", " live", date(year=2024, month=2, day=1), date(year=2024, month=3, day=1), 5, 3),
])
def test_models_GithubRepository_workflow_runs_success(
    slug:str, workflow:str, start:date, end:date, total:int, success:int,
    fixture_repository,
    fixture_workflow_runs_fixed_failures,
    ):
    """Test the simple workflow runs are return in a matching way"""

    # add patches for mocks
    with patch('models.github_repository.GithubRepository._repo') as repo_mock:
        repo_mock.return_value = fixture_repository(full_name=slug)

    with patch('models.github_repository.GithubRepository._workflow_runs') as workflow_runs_mock:
        workflow_runs_mock.return_value = fixture_workflow_runs_fixed_failures(total=total, success=success, start=start, end=end)

    g:Github = Github()
    repo = GithubRepository(g, slug)
    runs = repo.workflow_runs(workflow, 'main', start, end)
    # get just the good ones
    good = [d for d in runs if d.get('conclusion') == 'success']
    assert len(runs) == total
    assert len(good) == success


################################################
# REQUIRE GITHUB API CALLS TO BE MADE
# Will be skipped if GITHUB_ACCESS_TOKEN env var is not set
################################################




# @pytest.mark.parametrize("slug, branch, start, end, inrange",
# [
#     (
#         "ministryofjustice/serve-opg",
#         "main",
#         date(year=2024, month=2, day=1),
#         date(year=2024, month=3, day=1),
#         5
#     )
# ])
# @pytest.mark.skipif(os.environ.get("GITHUB_ACCESS_TOKEN", 0) == 0, reason="Requires real api calls, Github token env var (GITHUB_ACCESS_TOKEN) not present")
# def test_models_GithubRepository_pull_requests(slug:str, branch:str, start:date, end:date, inrange:int):
#     """Test that the class inits and the slugs / names all match"""
#     g:Github = Github()
#     repo = GithubRepository(g, slug)
#     all = repo.pull_requests(branch, start, end)
#     first = all[0]
#     pp(first)

#     assert len(all) == inrange
#     # assert isinstance(first._type, PullRequest) == True
