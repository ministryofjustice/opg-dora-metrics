import os
import pytest
from unittest.mock import patch
from datetime import date,datetime,timezone
from pprint import pp
from dateutil.relativedelta import relativedelta
from github import Github
from github.Repository import Repository
from github.Team import Team
from github.Artifact import Artifact
from github.WorkflowRun import WorkflowRun
from github.PullRequest import PullRequest
from github.PullRequestPart import PullRequestPart
from app.utils.dates.convert import to_date
from app.data.remote.github.localise import localise_artifacts,localise_pull_requests,localise_teams,localise_workflow_runs, localise_repo

from faker import Faker
from fake.github import repository, workflow_run, team, pull_request, artifact, attach
fake = Faker()
fake.add_provider(repository.FakeGithubRepositoryProvider)
fake.add_provider(workflow_run.FakeGithubWorkflowRunProvider)
fake.add_provider(team.FakeGithubTeamProvider)
fake.add_provider(pull_request.FakeGithubPullRequestProvider)
fake.add_provider(artifact.FakeGithubArtifactProvider)


def test_data_remote_github_localise_teams():
    """Test a fake team is localised correctly with matching details"""

    parent:Team = fake.github_team(real_values={'name':'OPG', 'slug':'opg'})
    teams:list[Team] = fake.github_teams(count=3)
    # attach the parent to the fake teams
    for t in teams:
        attach.attach_property(t, '_parent', parent)

    repo:Repository = fake.github_repository()
    with patch('app.data.remote.github.localise.teams', return_value=teams):
        localised, all_teams = localise_teams(repo)
        # make sure length matches
        assert len(teams) == len(localised)
        assert len(teams) == len(all_teams)
        # make sure parent id is mapped
        assert parent.id == localised[0]['parent_id']


def test_data_remote_github_localise_workflow_runs():
    """Check workflow locaisation and filtering"""
    e:date = datetime.now(timezone.utc).date() - relativedelta(months=5)
    s:date = e - relativedelta(months=2)
    # out of bound dates
    out_start:date = e + relativedelta(months=2)
    out_end:date = out_start + relativedelta(months=2)
    # fake runs made from a mix of both in and out of range and name matches
    repo:Repository = fake.github_repository(real_values={'full_name':'opg/test', 'name': 'test'})
    runs_in:list[WorkflowRun] = fake.github_workflow_runs(count=3, success=True, lower_date=s, upper_date=e, real_values={'name':'Path to Live'})
    runs_not_matched:list[WorkflowRun] = fake.github_workflow_runs(count=2, success=True, lower_date=s, upper_date=e, real_values={'name':'test run'})
    runs_out:list[WorkflowRun] = fake.github_workflow_runs(count=2, success=True, lower_date=out_start, upper_date=out_end, real_values={'name':'Path to Live'})
    runs:list[WorkflowRun] = runs_in + runs_out + runs_not_matched
    # attach all workflows to the fake repo
    for w in runs:
        attach.attach_property(w, '_repository', repo)

    with patch('app.data.remote.github.localise.workflow_runs', return_value=runs):
        l, all = localise_workflow_runs(repository=repo, start=s, end=e, status='success')
        # check lengths
        assert len(runs_in) == len(all)
        assert len(runs_in) == len(l)
        assert repo.id == l[0]['repository_id']


def test_data_remote_github_localise_artifacts():
    """Check workflow locaisation and filtering"""
    e:date = datetime.now(timezone.utc).date() - relativedelta(months=5)
    s:date = e - relativedelta(months=2)

    # fake runs made from a mix of both in and out of range and name matches
    repo:Repository = fake.github_repository(real_values={'full_name':'opg/test', 'name': 'test'})
    run:list[WorkflowRun] = fake.github_workflow_run(success=True, lower_date=s, upper_date=e, real_values={'name':'Path to Live'})
    artifacts:list[Artifact] = fake.github_artifacts(count=3)
    # attach all workflows to the fake repo

    attach.attach_property(run, '_repository', repo)
    for a in artifacts:
        attach.attach_property(a, '_workflow_run', run)

    with patch('app.data.remote.github.localise.artifacts', return_value=artifacts):
        l, all = localise_artifacts([run])
        assert len(artifacts) == len(l)
        assert len(artifacts) == len(all)
        assert run.id == l[0]['workflow_run_id']
        assert repo.id == l[0]['repository_id']


def test_data_remote_github_localise_pull_requests():
    """Check pr locaisation and filtering"""
    e:date = datetime.now(timezone.utc).date() - relativedelta(months=1)
    s:date = e - relativedelta(months=2)
    # out of bound dates
    out_start:date = e + relativedelta(years=1)
    out_end:date = out_start + relativedelta(months=2)

    repo:Repository = fake.github_repository(real_values={'full_name':'opg/test', 'name': 'test'})
    prs_in:list[PullRequest] = fake.github_pull_requests(lower_date=s, upper_date=e)
    prs_out:list[PullRequest] = fake.github_pull_requests(lower_date=out_start, upper_date=out_end)
    prs:list[PullRequest] = prs_in + prs_out
    base:PullRequestPart = fake.github_pull_request_base()

    # attach the repo to the base
    attach.attach_property(base, '_repo', repo)
    # attach the base to all prs
    for pr in prs:
        attach.attach_property(pr, '_base', base)

    # overwrite the call to fetch all prs with one that will return our fake data including out or range
    # prs so we can check they are filtered
    with patch('app.data.remote.github.pull_request.__pull_requests__', return_value=prs):
        l, all = localise_pull_requests(repository=repo, start=s, end=e)
        assert len(prs_in) == len(l)
        assert len(prs_in) == len(all)
        assert repo.id == l[0]['repository_id']


@pytest.mark.skipif(os.environ.get('GITHUB_TEST_TOKEN', 0) == 0, reason='Requires github token to run')
def test_data_remote_github_repository_to_local_using_real_repository():
    """Test the a real repository

    Using a fixed point in time, so these resources may be removed due to github data retention policies
    """

    g:Github = Github(os.environ.get('GITHUB_TEST_TOKEN'))
    repo:Repository = g.get_repo("ministryofjustice/serve-opg")

    local_repo, r = localise_repo(repo)
    assert repo.id == local_repo['id']
    assert repo.id == r.id


# @pytest.mark.parametrize(
#     "name, start, end",
#     [
#         ("serve-opg", '2023-04-01', '2023-04-30')
#     ]
# )
# def test_data_remote_github_repository_to_local_mocked(name:str, start:str, end:str):
#     """Test conversion to local repository using faked elements all the way down

#     By creating faked versions of associated date we can then check all are mapped over
#     correctly and test joining between the data sources
#     """
#     s:date = to_date(start, format='%Y-%m-%d')
#     e:date = to_date(end, format='%Y-%m-%d')
#     # out of bound dates
#     out_start:date = e + relativedelta(months=2)
#     out_end:date = out_start + relativedelta(months=2)

#     full_name:str = f'ministryofjustice/{name}'
#     fake_repo = fake.github_repository(real_values={'full_name':full_name, 'name': name})
#     fake_teams = fake.github_teams(count=2, real_values={'name':'OPG', 'slug':'opg'})
#     # fake runs made from a mix of both in and out of range
#     fake_runs_in = fake.github_workflow_runs(count=3, lower_date=s, upper_date=e, real_values={'name':'Path to Live'})
#     fake_runs_out = fake.github_workflow_runs(count=3, lower_date=out_start, upper_date=out_end, real_values={'name':'Path to Live'})
#     fake_runs = fake_runs_in + fake_runs_out

#     fake_prs = fake.github_pull_requests(lower_date=s, upper_date=e)
#     fake_artifacts = fake.github_artifacts(count=6, lower_date=s, upper_date=e)
#     # attach one workflow to an artifact
#     fake_artifacts[0] = attach.attach_property(fake_artifacts[0], '_workflow_run', fake_runs[0])

#     # # patch the call to fetch the repo to return a fake serve
#     # with patch('app.data.remote.github.to_local.get_repository_by_slug', return_value=fake_repo):
#     #     # patch the teams call so it returns a set number of fakes
#     #     with patch('app.data.remote.github.to_local.teams', return_value=fake_teams):
#     #         # patch finding workflows to return ones with path to live as its name
#     #         with patch('app.data.remote.github.to_local.workflow_runs', return_value=fake_runs):
#     #             # patch finding pull requests
#     #             with patch('app.data.remote.github.to_local.merged_pull_requests', return_value=fake_prs):
#     #                 # patch artifacts
#     #                 with patch('app.data.remote.github.to_local.artifacts', return_value=fake_artifacts):
#     #                     # now convert!
#     #                     g:Github = Github()



#     #                     data = to_local(g=g,
#     #                                     repository="ministryofjustice/serve-opg",
#     #                                     start=s,
#     #                                     end=e,
#     #                                     get_artifacts=True,
#     #                                     get_pull_requests=True,
#     #                                     )
#     #                     assert name == data.get('name')
#     #                     assert full_name == data.get('full_name')
#     #                     # teams
#     #                     assert len(fake_teams) == len(data.get('teams'))
#     #                     assert 'opg' == data.get('teams')[0].get('slug')
#     #                     # workflows - should only get ones in range
#     #                     assert len(fake_runs_in) == len(data.get('workflow_runs'))
#     #                     # prs
#     #                     assert len(fake_prs) == len(data.get('pull_requests'))
#     #                     # artifacts
#     #                     assert len(fake_artifacts) == len(data.get('artifacts'))
#     #                     # check the joining worked
#     #                     assert 1 == len(data.get('workflow_runs')[0]['artifacts'])
