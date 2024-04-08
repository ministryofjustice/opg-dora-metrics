import pytest
import random
from typing import Any
from datetime import date, timedelta
from unittest.mock import patch

from faker import Faker

from github import Github
from github.PullRequest import PullRequest
from github.WorkflowRun import WorkflowRun
from github.Repository import Repository

from models.github_repository import GithubRepository
from converter.convert import to, remapper
from log.logger import logging
from utils.dates import between, to_date, to_datetime

from tests.factory import faux


from pprint import pp

################################################
# Fixtures
################################################

@pytest.fixture
def fixture_repository():
    """Provide a Repository instance, can pass named params to set attrs:
    Example:
    fixture_repository(full_name='test')
    """
    def create(**kwargs) -> Repository:
        return faux.New(Repository, **kwargs)
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
            conclusion = 'success' if i < success else 'failure'
            wfr = faux.New(WorkflowRun, start=start, end=end, name=name, conclusion=conclusion)
            runs.append(wfr)

        # items outside of range
        for i in range(extras):
            wfr = faux.New(WorkflowRun, start='-50y', end=start - timedelta(days=-5) , name=name)
            runs.append(wfr)
        return runs
    return create


@pytest.fixture
def fixture_prs_in_range():
    """Provide a fixture to generate a list of fake pull requests
    """
    def create(branch:str, start:date, end:date, number_to_be_in_range:int) -> list[PullRequest]:
        prs: list[PullRequest] = []
        count:int = random.randint(number_to_be_in_range, number_to_be_in_range*2)
        logging.warn('creating faker prs', count=count)

        for i in range(count):
            if i < number_to_be_in_range:
                pull = faux.New(PullRequest, start=start, end=end, branch=branch, state='closed')
            else:
                pull = faux.New(PullRequest, start='-20y', end=start - timedelta(days=-10), branch=branch, state='closed')
            prs.append(pull)
        return prs
    return create


@pytest.fixture
def fixture_pr_items():
    """Create a series of Item objects based on PullRequest faked data"""
    def create(branch:str, start:date, end:date, count:int) -> list[dict]:
        """"""
        prs: list[dict] = []
        logging.warn('creating faker pr items', count=count)

        for i in range(count):
            pull = faux.New(PullRequest, start=start, end=end, branch=branch, state='closed')
            item = to(pull, remap=[remapper('merged_at', 'date'), remapper('state', 'status', lambda x: ('success')) ])
            prs.append(item)
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
            in_range = repo._parse_workflow_runs(all_runs, workflow, start, end )
            # should have x in range
            assert len(in_range) == total
            # get just the successful runs
            good = [d for d in in_range if d.get('status') == 'success']
            assert len(good) == success



@pytest.mark.parametrize(
    "slug, branch, start, end, inrange",
    [
        ("ministryofjustice/serve-opg", "main", date(year=2024, month=2, day=1), date(year=2024, month=3, day=1), 5),
        ("ministryofjustice/opg-github-actions", "main", date(year=2024, month=1, day=1), date(year=2024, month=2, day=1), 10),
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
            #### SOMETIMES GET FAILURES???
            if len(all) <= inrange:
                print(f'len:{len(all)} inrange:{inrange}')
                for v in all:
                    pp(v)

            # should have more than asked for
            assert (len(all) >= inrange) == True

            # reduce to juse in range
            found = repo._parse_pull_requests(all, branch, start, end)
            # check matches
            assert len(found) == inrange


@pytest.mark.parametrize(
    "slug, branch, start, end, total",
    [
        ("ministryofjustice/opg-lpa", "main", date(year=2023, month=6, day=1), date(year=2024, month=3, day=1), 30),
    ]
)
def test_models_GithubRepository_deployment_frequency_no_workflows(
    slug:str, branch:str, start:date, end:date, total:int,
    fixture_repository,
    fixture_pr_items,
    ):
    """Test correct number of items are returned, all as pull request and all within range"""

    # path the repo setup call
    with patch('models.github_repository.GithubRepository._repo', return_value=fixture_repository(full_name=slug)) :
        g:Github = Github()
        repo = GithubRepository(g, slug)
        # check name
        assert repo.r.full_name == slug
        # force the workflow runs to be empty and therefore call the merge count
        with patch('models.github_repository.GithubRepository.workflow_runs', return_value=[]):
            # replace the pull request data with fixture data
            with patch.object(
                repo, 'pull_requests',
                return_value=fixture_pr_items(branch=branch, start=start, end=end, count=total)):
                # now test the segments of the deployment frequency setup
                data:list[dict] = repo.pull_requests(branch, start, end, 'closed')

                # check the grouping is all in range
                grouped = repo._groupby(data, start, end)

                for ym, d in grouped.items():
                    assert between ( to_datetime(ym) , start, end) == True

                # check the totals match
                count = 0
                success = 0
                totals = repo._totals(grouped, 'status')

                for ym, data in totals.items():
                    count += data.get('total')
                    success += data.get('total_success')
                # check number matches what we expect from the generated set
                # - as these are pull requests, they should all be a success
                assert total == count == success

                # check the averages
                avg = repo._averages(totals)
                pp(avg)
