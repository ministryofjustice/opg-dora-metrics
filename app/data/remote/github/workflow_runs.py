import re
from datetime import date
from github import Github
from github.Repository import Repository
from github.WorkflowRun import WorkflowRun
from app.utils.dates.ranges import Increment, date_range_as_strings


def __workflow_runs__(repository:Repository, branch:str, date_range:str, status:str='success') -> list[WorkflowRun]:
    """Return a list of workflow runs for the repo in the date range set"""    
    return [wf for wf in repository.get_workflow_runs(branch=branch, created=date_range, status=status)]


def workflow_runs(
        repository:Repository,
        branch:str,
        start:date,
        end:date,
        status:str = 'success'
        ) -> list[WorkflowRun]:
    """As workflow api end point is rate limited, we need to put boundaries on the calls made.

    We use a set time period (described by start & end parameters) and chunk that into months,
    making an api call for each month to reduce call count
    """
    all:list[WorkflowRun] = []
    dates:list[str] = date_range_as_strings(start=start, end=end, inc=Increment.MONTH)

    for ym in dates:
        date_range:str = f'{ym}..{ym}'        
        runs:list[WorkflowRun] = __workflow_runs__(repository=repository, branch=branch, 
                                                   date_range=date_range, status=status)
        all += runs
    return all

def matching_workflow_runs(pattern:str, 
                           workflow_runs:list[WorkflowRun]) -> list[WorkflowRun]:
    """Reduce the list of workflow runs to those that match the pattern"""
    matched:list[WorkflowRun] = []
    total:int = len(workflow_runs)
    for i, wf in enumerate(workflow_runs):        
        pattern_match:bool = bool(re.search(pattern, wf.name.lower())) if pattern is not None else True
        if pattern_match:            
            matched.append(wf)
    return matched 
