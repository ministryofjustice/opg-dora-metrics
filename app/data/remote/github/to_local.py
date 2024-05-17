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
from app.data.remote.github.repository import repo
from app.data.remote.github.workflow_run import workflow_runs, matching_workflow_runs
from app.data.remote.github.pull_requst import merged_pull_requests
from app.data.local.github_data.map import Local
from app.log.logger import logging

def to_local(g:Github,
          reopsitory_slug:str,           
          start:date,
          end:date,
          workflow_run_pattern:str|None = ' live',
          get_artifacts:bool = False,
          get_pull_requests:bool = False,
          pull_request_fallback:bool = True) -> dict[str, Any]:
    """Use the remote data to generate a local version"""

    ########################  
    # Remote data
    ########################
    logging.info(f'[{reopsitory_slug}] getting remote data')
    repository:Repository = repo(g, reopsitory_slug)
    branch:str = repository.default_branch
    # init all the lists
    all_teams:list[Team] = []
    all_workflow_runs:list[WorkflowRun] = []
    matching_workflows:list[WorkflowRun] = []
    artfact_data:list[Artifact] = []
    pull_requests:list[PullRequest] = []
    # get all the teams
    all_teams = teams(repository=repository)
    # get all the workflows in the data range
    if workflow_run_pattern is not None:
        all_workflow_runs = workflow_runs(repository=repository,
                                          branch=branch,
                                          start=start,
                                          end=end)
        # reduce that to the matching workflows
        matching_workflows = matching_workflow_runs(pattern=workflow_run_pattern, 
                                                    workflow_runs=all_workflow_runs)
    # # get pull requests
    # # fetch them is asked, or if the fallback is set and we didnt find and workflow runs
    # if get_pull_requests is True or (pull_request_fallback is True and len(matching_workflows) == 0):
    #     pull_requests = merged_pull_requests(repository=repository, 
    #                                          branch=branch, 
    #                                          start=start,
    #                                          end=end)

    # # get artifact data
    # if get_artifacts:
    #     for wf in matching_workflows:
    #         artfact_data.extend(artifacts(wf))

    ########################  
    # Local data - reducing down to dict
    ########################
    logging.info(f'[{reopsitory_slug}] localising')
    local_teams:list[dict[str,Any]] = [Local(t) for t in all_teams]
    local_workflows:list[dict[str,Any]] = [Local(wf) for wf in matching_workflows]
    # local_pull_requests:list[dict[str,Any]] = [Local(pr) for pr in pull_requests]
    # local_artifacts:list[dict[str,Any]] = [Local(artifact) for artifact in artfact_data]    
    # if get_artifacts:
    #     # merge the artifacts into the workflows
    #     for item in local_workflows:
    #         item['artifacts'] = [a for a in local_artifacts if a['workflow_run_id'] == item['id']]
        
    local_repository:dict[str,Any] = Local(repository)
    # ## now extended that with extra local data
    local_repository['teams'] = local_teams
    local_repository['workflow_runs'] = local_workflows
    # local_repository['artifacts'] = local_artifacts
    # local_repository['pull_requests'] = local_pull_requests
    return local_repository

    
    


