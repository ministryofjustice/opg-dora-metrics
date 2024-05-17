import os
import pytest
from unittest.mock import patch
from datetime import date
from pprint import pp
from dateutil.relativedelta import relativedelta
from github import Github
from github.Repository import Repository
from app.utils.dates.convert import to_date
from app.data.local.github_data.map import Local
from app.data.remote.github.to_local import to_local

from faker import Faker
from fake.github import repository, workflow_run, team, pull_request, artifact, attach
fake = Faker()
fake.add_provider(repository.FakeGithubRepositoryProvider)
fake.add_provider(workflow_run.FakeGithubWorkflowRunProvider)
fake.add_provider(team.FakeGithubTeamProvider)
fake.add_provider(pull_request.FakeGithubPullRequestProvider)
fake.add_provider(artifact.FakeGithubArtifactProvider)


@pytest.mark.skipif(os.environ.get('GITHUB_TEST_TOKEN', 0) == 0, reason='Requires github token to run')
def test_data_remote_github_repository_to_local_using_real_repository():
    """Test the a real repository
    
    Using a fixed point in time, so these resources may be removed due to github data retention policies
    """
    
    g:Github = Github(os.environ.get('GITHUB_TEST_TOKEN'))
    data = to_local(g=g, 
                    reopsitory_slug="ministryofjustice/serve-opg",
                    start=date(year=2024, month=4, day=1),
                    end=date(year=2024, month=4, day=30),
                    get_artifacts=True,
                    get_pull_requests=True,
                    )
    # test against real world known values
    assert 21 == len(data.get('workflow_runs'))
    assert 21 == len(data.get('artifacts'))
    assert False == data['archived']
    assert 'main' == data['default_branch']
    # make sure known pr is in there
    found:bool = False
    known_id = 1845603630
    for p in data['pull_requests']:        
        if p['id'] == known_id:
            found = True
    assert True == found
    
@pytest.mark.parametrize(
    "name, start, end",
    [
        ("ministryofjustice/serve-opg", '2023-04-01', '2023-04-30')
    ]
)
def test_data_remote_github_repository_to_local_mocked(name:str, start:str, end:str):
    """Test conversion to local repository using faked elements all the way down

    By creating faked versions of associated date we can then check all are mapped over 
    correctly and test joining between the data sources    
    """
    s:date = to_date(start, format='%Y-%m-%d')
    e:date = to_date(end, format='%Y-%m-%d')    
    # out of bound dates
    out_start:date = e + relativedelta(months=2)
    out_end:date = out_start + relativedelta(months=2)

    full_name:str = f'ministryofjustice/{name}'
    fake_repo = fake.github_repository(real_values={'full_name':full_name, 'name': name})
    fake_teams = fake.github_teams(count=2, real_values={'name':'OPG', 'slug':'opg'})
    # fake runs made from a mix of both in and out of range
    fake_runs_in = fake.github_workflow_runs(count=3, lower_date=s, upper_date=e, real_values={'name':'Path to Live'})
    fake_runs_out = fake.github_workflow_runs(count=3, lower_date=out_start, upper_date=out_end, real_values={'name':'Path to Live'})
    fake_runs = fake_runs_in + fake_runs_out

    fake_prs = fake.github_pull_requests(lower_date=s, upper_date=e)
    fake_artifacts = fake.github_artifacts(count=6, lower_date=s, upper_date=e)
    # attach one workflow to an artifact
    fake_artifacts[0] = attach.attach_property(fake_artifacts[0], '_workflow_run', fake_runs[0])
    
    # patch the call to fetch the repo to return a fake serve
    with patch('app.data.remote.github.to_local.repo', return_value=fake_repo):
        # patch the teams call so it returns a set number of fakes
        with patch('app.data.remote.github.to_local.teams', return_value=fake_teams):
            # patch finding workflows to return ones with path to live as its name
            with patch('app.data.remote.github.to_local.workflow_runs', return_value=fake_runs):
                # patch finding pull requests
                with patch('app.data.remote.github.to_local.merged_pull_requests', return_value=fake_prs):
                    # patch artifacts
                    with patch('app.data.remote.github.to_local.artifacts', return_value=fake_artifacts):
                        # now convert!
                        g:Github = Github()
                        data = to_local(g=g, 
                                        reopsitory_slug="ministryofjustice/serve-opg",
                                        start=s,
                                        end=e,
                                        get_artifacts=True,
                                        get_pull_requests=True,
                                        )
                        assert name == data.get('name')
                        assert full_name == data.get('full_name')
                        # teams
                        assert len(fake_teams) == len(data.get('teams'))
                        assert 'opg' == data.get('teams')[0].get('slug')
                        # workflows - should only get ones in range
                        assert len(fake_runs_in) == len(data.get('workflow_runs'))                    
                        # prs
                        assert len(fake_prs) == len(data.get('pull_requests'))
                        # artifacts
                        assert len(fake_artifacts) == len(data.get('artifacts'))
                        # check the joining worked
                        assert 1 == len(data.get('workflow_runs')[0]['artifacts'])


