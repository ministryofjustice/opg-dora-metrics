from typing import Any
from datetime import date
from pprint import pp

from github import Github
from github.Repository import Repository
from github.Team import Team
from github.Artifact import Artifact
from github.WorkflowRun import WorkflowRun

from app.data.remote.github.artifact import artifacts
from app.data.remote.github.team import teams
from app.data.remote.github.repository import repo
from app.data.remote.github.workflow_run import workflow_runs, matching_workflow_runs

from app.data.local.github_data.map import Local

def to_local(g:Github,
          reopsitory_slug:str,           
          start:date,
          end:date,
          workflow_pattern:str = ' live',
          get_artifacts:bool = False) -> dict[str, Any]:
    """Use the remote data to generate a local version"""

    repository:Repository = repo(g, reopsitory_slug)
    branch:str = repository.default_branch
    # get all the teams
    all_teams:list[Team] = teams(repository=repository)
    # get all the workflows in the data range
    all_workflow_runs:list[WorkflowRun] = workflow_runs(repository=repository,
                                                        branch=branch,
                                                        start=start,
                                                        end=end)
    # reduce that to the matching workflows
    matching_workflows:list[WorkflowRun] = matching_workflow_runs(pattern=workflow_pattern, 
                                                                  workflow_runs=all_workflow_runs)
    # get artifact data
    artfact_data:list[Artifact] = []
    if get_artifacts:
        for wf in matching_workflows:
            artfact_data.extend(artifacts(wf))

    ## now localise the data    
    local_teams:list[dict[str,Any]] = [Local(t) for t in all_teams]
    local_workflows:list[dict[str,Any]] = [Local(wf) for wf in matching_workflows]
    local_artifacts:list[dict[str,Any]] = []
    if get_artifacts and len(artfact_data) > 0:
        local_artifacts = [Local(artifact) for artifact in artfact_data]
        # merge the artifacts into the workflows
        for item in local_workflows:
            item['artifacts'] = [a for a in local_artifacts if a['workflow_run_id'] == item['id']]
        
    local_repository:dict[str,Any] = Local(repository)
    ## now extended that with extra local data
    local_repository['workflow_runs'] = local_workflows
    local_repository['teams'] = local_teams
    local_repository['artifacts'] = local_artifacts
    
    return local_repository

    
    


