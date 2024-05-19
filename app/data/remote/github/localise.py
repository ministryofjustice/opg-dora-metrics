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

# @timer
# def to_local(g:Github,
#           repository:str|Repository,
#           start:date = None,
#           end:date = None,
#           get_teams:bool = True,
#           get_artifacts:bool = False,
#           get_pull_requests:bool = False,
#           get_workflow_runs:bool = True,
#           workflow_run_pattern:str|None = ' live',
#           workflow_run_status:str= 'success',
#           pull_request_fallback:bool = True) -> dict[str, Any]:
#     """Use the remote data to generate a local version"""

#     ########################
#     # Remote data
#     ########################
#     repo:Repository = None

#     if type(repository) is str:
#         repo:Repository = get_repository_by_slug(g, repository)
#     else:
#         repo:Repository = repository
#     # make sure we have a repo
#     assert isinstance(repo, Repository)

#     logging.info(f'[{repo.full_name}] getting remote data')

#     branch:str = repo.default_branch
#     # init all the lists
#     all_teams:list[Team] = []
#     all_workflow_runs:list[WorkflowRun] = []
#     matching_workflows:list[WorkflowRun] = []
#     artifact_data:list[Artifact] = []
#     pull_requests:list[PullRequest] = []
#     # get all the teams
#     all_teams = teams(repository=repo) if get_teams is True else []
#     # get all the workflows in the data range
#     if get_workflow_runs is True and workflow_run_pattern is not None:
#         all_workflow_runs = workflow_runs(repository=repo,
#                                           branch=branch,
#                                           status=workflow_run_status,
#                                           start=start,
#                                           end=end)
#         # in range
#         runs_in_range = workflow_runs_in_range(start=start,
#                                                end=end,
#                                                workflow_runs=all_workflow_runs)
#         # reduce that to the matching workflows
#         matching_workflows = matching_workflow_runs(pattern=workflow_run_pattern,
#                                                     workflow_runs=runs_in_range)
#     # get pull requests
#     # fetch them is asked, or if the fallback is set and we didnt find and workflow runs
#     if get_pull_requests is True or (pull_request_fallback is True and len(matching_workflows) == 0):
#         pull_requests = merged_pull_requests(repository=repo,
#                                              branch=branch,
#                                              start=start,
#                                              end=end)

#     # get artifact data
#     if get_artifacts:
#         for wf in matching_workflows:
#             artifact_data.extend(artifacts(wf))

#     ########################
#     # Local data - reducing down to dict
#     ########################
#     logging.info(f'[{repo.full_name}] localising')
#     local_teams:list[dict[str,Any]] = [Local(t) for t in all_teams]
#     local_workflows:list[dict[str,Any]] = [Local(wf) for wf in matching_workflows]
#     local_pull_requests:list[dict[str,Any]] = [Local(pr) for pr in pull_requests]
#     # make artifacts unique
#     uni:dict[str, dict[str,Any]] = {a.id:a for a in artifact_data}
#     local_artifacts:list[dict[str,Any]] = [Local(artifact) for id, artifact in uni.items()]

#     # merge the artifacts into the workflows
#     if get_artifacts:
#         for item in local_workflows:
#             item['artifacts'] = [a for a in local_artifacts if a['workflow_run_id'] == item['id']]

#     local_repository:dict[str,Any] = Local(repo)
#     # ## now extended that with extra local data
#     local_repository['teams'] = local_teams
#     local_repository['workflow_runs'] = local_workflows
#     local_repository['pull_requests'] = local_pull_requests
#     local_repository['artifacts'] = local_artifacts

#     return local_repository
