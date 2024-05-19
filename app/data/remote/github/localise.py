from typing import Any
from datetime import date
from pprint import pp
from github import Github
from github.Repository import Repository
from github.Team import Team
from github.Artifact import Artifact
from github.WorkflowRun import WorkflowRun
from github.PullRequest import PullRequest

from app.data.remote.github.artifact import artifacts
from app.data.remote.github.team import teams
from app.data.remote.github.repository import get_repository_by_slug
from app.data.remote.github.workflow_run import workflow_runs, matching_workflow_runs, workflow_runs_in_range
from app.data.remote.github.pull_request import merged_pull_requests
from app.data.local.github_data.map import Local
from app.log.logger import logging
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
    all:list[PullRequest] = merged_pull_requests(repository=repository, branch=branch, start=start, end=end)
    localised:list[dict] = [Local(pr) for pr in all]
    return localised, all

@timer
def localise_teams(repository:Repository) -> tuple[list[dict], list[Team]]:
    """Localise teams"""
    all:list[Team] = teams(repository=repository)
    localised:list[dict] = [Local(team) for team in all]
    return localised, all

@timer
def localise_repo(repository:Repository) -> tuple[dict, Repository]:
    """Localise repo"""
    return Local(repository), repository
