import pytest
import random
from datetime import date, datetime, timedelta
from unittest.mock import patch

from faker import Faker

from github import Github
from github.PullRequest import PullRequest
from github.WorkflowRun import WorkflowRun
from github.Repository import Repository

from models.github_repository import GithubRepository, KeepWorkflowRunFields, KeepPullRequestFields
from models.item import Item
from models.keep import attrs
from log.logger import logging


from pprint import pp

################################################
# Faker methods to generate skel valid objects
################################################

fake = Faker()


################################################
# Fixtures & side effects
################################################




@pytest.fixture
def fixture_repository():
    """Provide a Repository instance, can pass named params to set attrs:
    Example:
    fixture_repository(full_name='test')
    """
    def create(**kwargs) -> Repository:
        logging.info('creating faker repository')
        return Repository(requester=None, headers={}, attributes=kwargs, completed=True)
    return create

@pytest.fixture
def fixture_workflow_run():
    """Provide a WorkflowRun instance, can pass named params to set attrs:

    Example:
    fixture_workflow_run(full_name='test')
    """
    def create(**kwargs) -> WorkflowRun:
        return WorkflowRun(requester=None, headers={}, attributes=kwargs, completed=True)
    return create

@pytest.fixture
def fixture_workflow_runs_in_range():
    """Provide a list of WorkflowRun instances that have a created_at date between start & end,
    a random name. Will set the first `success` number of instances to have conclusion='success'
    """
    def create(name:str, total:int, success:int, start:date, end:date, extras:int) -> list[WorkflowRun]:
        logging.warn('creating faker workflow runs', count=total)
        runs: list[WorkflowRun] = []
        # items within the date range
        for i in range(total):
            dt:datetime = fake.date_between(start_date=start, end_date=end)
            props = {
                'id': fake.random_number(),
                'created_at': dt.isoformat(),
                'name': fake.sentence(nb_words=4) + name,
                'conclusion': 'success' if i < success else 'failure'
            }
            runs.append(
                WorkflowRun(requester=None, headers={}, attributes=props, completed=True)
            )
        # items outside of range
        for i in range(extras):
            dt:datetime = fake.date_between(start_date='-50y', end_date=start - timedelta(days=-5))
            props = {
                'id': fake.random_number(),
                'created_at': dt.isoformat(),
                'name': fake.sentence(nb_words=4) + name,
                'conclusion': 'success'
            }
            runs.append(
                WorkflowRun(requester=None, headers={}, attributes=props, completed=True)
            )

        return runs
    return create


@pytest.fixture
def fixture_prs_in_range():
    """
    """
    def create(branch:str, start:date, end:date, number_to_be_in_range:int) -> list[PullRequest]:
        """"""
        prs: list[PullRequest] = []
        count:int = random.randint(number_to_be_in_range, number_to_be_in_range*2)
        logging.warn('creating faker prs', count=count)

        for i in range(count):
            if i < number_to_be_in_range:
                dt:datetime = fake.date_between(start_date=start, end_date=end)
            else:
                dt:datetime = fake.date_between(start_date='-20y', end_date=start - timedelta(days=-10))
            attrs = {
                'id': fake.random_number(),
                'number': fake.random_number(),
                'branch': branch,
                'merged_at': dt.isoformat(),
                'title': fake.sentence(nb_words=4),
                'state': 'closed'
            }
            prs.append(PullRequest(requester=None, headers={}, attributes=attrs, completed=True))
        return prs
    return create


################################################
# Tests
################################################
@pytest.mark.parametrize(
    "slug",
    [
        ("ministryofjustice/serve-opg")
    ]
)
def test_models_GithubRepository_init_success(slug:str, fixture_repository):
    """Test that the class inits and the slugs / names all match"""

    with patch('models.github_repository.GithubRepository._repo') as repo_mock:
        repo_mock.return_value = fixture_repository(full_name=slug, id=111)

        g:Github = Github()
        repo = GithubRepository(g, slug)
        assert repo.r.id == 111
        assert repo.r.full_name == slug
        assert repo.name() == slug


@pytest.mark.parametrize(
    "slug, workflow, start, end, total, success",
    [
        ("ministryofjustice/serve-opg", " live", date(year=2024, month=2, day=1), date(year=2024, month=3, day=1), 5, 1),
    ]
)
def test_models_GithubRepository_workflow_runs_success(
    slug:str, workflow:str, start:date, end:date, total:int, success:int,
    fixture_repository,
    fixture_workflow_runs_in_range,
    ):
    """Test the workflow runs return data and that data is filtered based on dates and the pattern passed

    Mock repo creation and the fetching of getting the workflow runs
    """

    # patch the github repo call for when we create a new instance
    with patch('models.github_repository.GithubRepository._repo', return_value=fixture_repository(full_name=slug)) :

        g:Github = Github()
        repo = GithubRepository(g, slug)
        assert repo.r.full_name == slug
        # patch this instance of GithubRepository _get_workflow_runs to return series of mocked data
        # via the return_value
        # always have 2 extra that are outside of data range
        extras:int = 2
        with patch.object(
            repo, '_get_workflow_runs',
            return_value=fixture_workflow_runs_in_range(name=workflow, total=total, success=success, start=start, end=end, extras=extras)) :
            # fetch all runs
            all_runs = repo._get_workflow_runs(workflow, 'main', f'{start}..{end}')
            # should have more
            assert len(all_runs) == (total + extras)
            # now prune
            in_range = repo._parse_workflow_runs(all_runs, attrs(WorkflowRun) , workflow, start, end )
            # should have x in range
            assert len(in_range) == total
            # get just the successful runs
            good = [d for d in in_range if d.get('conclusion') == 'success']
            assert len(good) == success



@pytest.mark.parametrize(
    "slug, branch, start, end, inrange",
    [
        ("ministryofjustice/serve-opg", "main", date(year=2024, month=2, day=1), date(year=2024, month=3, day=1), 5)
    ]
)
def test_models_GithubRepository_pull_requests(
    slug:str, branch:str, start:date, end:date, inrange:int,
    fixture_repository,
    fixture_prs_in_range
    ):
    """Test a mocked out version of pull requests that dont hit the github api

    Check they are process and filtered to date ranges and types are tracked
    """

    # path the repo setup call
    with patch('models.github_repository.GithubRepository._repo', return_value=fixture_repository(full_name=slug)) :
        g:Github = Github()
        repo = GithubRepository(g, slug)
        assert repo.r.full_name == slug

        # patch the instance we created
        with patch.object(
            repo, '_get_pull_requests',
            return_value= fixture_prs_in_range(branch=branch, start=start, end=end, number_to_be_in_range=inrange)
            ) :

            all = repo._get_pull_requests(branch)
            # should have more than asked for
            assert (len(all) > inrange) == True
            # reduce to juse in range
            found = repo._parse_pull_requests(all, attrs(PullRequest), branch, start, end)
            # check matches
            assert len(found) == inrange
            # get first item and check type
            first = found[0]
            assert first._type == PullRequest


# @pytest.mark.parametrize(
#     "slug, branch, start, end",
#     [
#         ("ministryofjustice/opg-lpa", "main", date(year=2024, month=1, day=1), date(year=2024, month=3, day=1))
#     ]
# )
# def test_models_GithubRepository_deployment_frequency(slug:str, branch:str, start:date, end:date):
#     """"""
#     g:Github = Github()
#     repo = GithubRepository(g, slug)
#     repo.deployment_frequency(start, end, branch=branch)
