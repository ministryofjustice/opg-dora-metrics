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
from app.dates.convert import to_date
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
    prs:list[PullRequest] = fake.github_pull_requests(lower_date=s, upper_date=e)
    base:PullRequestPart = fake.github_pull_request_base()

    # attach the repo to the base
    attach.attach_property(base, '_repo', repo)
    # attach the base to all prs
    for pr in prs:
        attach.attach_property(pr, '_base', base)

    # overwrite the call to fetch all prs with one that will return our fake data including out or range
    # prs so we can check they are filtered
    with patch('app.data.remote.github.pull_request.__pull_requests_in_range__', return_value=prs):
        l, all = localise_pull_requests(repository=repo, start=s, end=e)
        assert len(prs) == len(l)
        assert len(prs) == len(all)
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
