import os
import pytest
from unittest.mock import patch
from datetime import date
from pprint import pp

from github import Github
from github.Repository import Repository
from app.data.local.github_data.map import Local
from app.data.remote.github.to_local import to_local

from faker import Faker
from fake.github import repository, workflow_run, team, pull_request
fake = Faker()
fake.add_provider(repository.FakeGithubRepositoryProvider)
fake.add_provider(workflow_run.FakeGithubWorkflowRunProvider)
fake.add_provider(team.FakeGithubTeamProvider)
fake.add_provider(pull_request.FakeGithubPullRequestProvider)



@pytest.mark.skipif(os.environ.get('GITHUB_TEST_TOKEN', 0) == 0, reason='Requires github token to run')
def test_data_remote_github_repository_to_local_using_real_repository():
    """Test the a real repository"""
    
    g:Github = Github(os.environ.get('GITHUB_TEST_TOKEN'))
    data = to_local(g=g, 
                    reopsitory_slug="ministryofjustice/serve-opg",
                    start=date(year=2024, month=4, day=1),
                    end=date(year=2024, month=4, day=30),
                    get_artifacts=True,
                    get_pull_requests=True,
                    )
    pp(data)
    # test against real world known values
    assert 23 == len(data.get('workflow_runs'))
    assert 23 == len(data.get('artifacts'))
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
    "name",
    [
        ("ministryofjustice/serve-opg")
    ]
)
def test_data_remote_github_repository_to_local_mocked(name:str):
    """Test conversion to local repository using faked elements all the way down
    fake:
        - Repository
        - Team
        - WorkflowRun
        - todo: PullRequests
        - todo: Artifacts
    """
    full_name:str = f'ministryofjustice/{name}'
    # patch the call to fetch the repo to return a fake serve
    with patch('app.data.remote.github.to_local.repo', 
               return_value=fake.github_repository(real_values={'full_name':full_name, 'name': name})):
        # patch the teams call so it returns a set number of fakes
        with patch('app.data.remote.github.to_local.teams', 
                   return_value=fake.github_teams(real_values={'name':'OPG', 'slug':'opg'})):
        
            # patch finding workflows to return ones with path to live as its name
            with patch('app.data.remote.github.to_local.workflow_runs', 
                       return_value=fake.github_workflow_runs(real_values={'name':'Path to Live'})):
                
                g:Github = Github()
                data = to_local(g=g, 
                            reopsitory_slug="ministryofjustice/serve-opg",
                            start=date(year=2024, month=4, day=1),
                            end=date(year=2024, month=4, day=30),
                            get_artifacts=True,
                            get_pull_requests=True,
                            )
                pp(data)
                assert name == data.get('name')
                assert full_name == data.get('full_name')
                # teams
                assert 1 == len(data.get('teams'))
                assert 'opg' == data.get('teams')[0].get('slug')
                # workflows
                assert 1 == len(data.get('workflow_runs'))


