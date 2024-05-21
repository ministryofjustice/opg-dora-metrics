from typing import Any
from datetime import date
from pprint import pp
from github import Github
from github.Repository import Repository
from github.Team import Team
from github.Artifact import Artifact
from github.WorkflowRun import WorkflowRun
from github.PullRequest import PullRequest

from app.data.github.remote.artifact import artifacts
from app.data.github.remote.team import teams
from app.data.github.remote.workflow_run import workflow_runs, matching_workflow_runs, workflow_runs_in_range
from app.data.github.remote.pull_request import pull_requests_in_range
from app.data.github.local.map import Local
from app.logger import logging
from app.decorator import timer

@timer
def localise_workflow_runs(repository:Repository,
                           start:date,
                           end:date,
                           branch:str='main',
                           pattern:str= ' live$',
                           status:str= 'success') -> tuple[list[dict], list[WorkflowRun]]:
    """Find all the workflows for the repository that match dates and pattern and return local versions"""
    all:list[WorkflowRun] = workflow_runs(repository=repository,
                                          branch=branch,
                                          start=start,
                                          end=end,
                                          status=status)
    in_range:list[WorkflowRun] = workflow_runs_in_range(start=start,
                                                       end=end,
                                                       workflow_runs=all)
    matched:list[WorkflowRun] = matching_workflow_runs(pattern=pattern, workflow_runs=in_range)
    localised:list[dict] = [Local(wfr) for wfr in matched]
    return localised, matched

@timer
def localise_artifacts(workflow_runs:list[WorkflowRun]) -> tuple[list[dict], list[Artifact]]:
    """Create a localised series of artifacts based on the workflow run data"""
    all:list[Artifact] = []
    for wfr in workflow_runs:
        all.extend(artifacts(wfr))
    localised:list[dict] = [Local(artifact) for artifact in all]
    return localised, all

@timer
def localise_pull_requests(repository:Repository,
                           start:date,
                           end:date,
                           branch:str='main') -> tuple[list[dict], list[PullRequest]]:
    """Localisation of pull requests"""
    in_range:list[PullRequest] = pull_requests_in_range(repository=repository, branch=branch, start=start, end=end)

    localised:list[dict] = [Local(pr) for pr in in_range]
    return localised, in_range

@timer
def localise_teams(repository:Repository, filter_by_parent_slug:str=None) -> tuple[list[dict], list[Team]]:
    """Localise teams"""
    all:list[Team] = teams(repository=repository, filter_by_parent_slug=filter_by_parent_slug)
    localised:list[dict] = [Local(team) for team in all]
    return localised, all

@timer
def localise_repo(repository:Repository) -> tuple[dict, Repository]:
    """Localise repo"""
    return Local(repository), repository
