import re
from datetime import date
from github import Github
from github.Repository import Repository
from github.WorkflowRun import WorkflowRun
from app.utils.dates.ranges import Increment, date_range_as_strings
from app.log.logger import logging


def __workflow_runs__(repository:Repository, branch:str, date_range:str, status:str='success') -> list[WorkflowRun]:
    """Return a list of workflow runs for the repo in the date range set"""    
    logging.debug('getting workflow runs for date_range', repo=repository.full_name, date_range=date_range, status=status, branch=branch)
    runs:list[WorkflowRun] = [wf for wf in repository.get_workflow_runs(branch=branch, created=date_range, status=status)]
    logging.debug(f'[{repository.full_name}] (workflow_runs) found [{len(runs)}] workflow_runs in date_range',  repo=repository.full_name, date_range=date_range, status=status, branch=branch)
    return runs


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
    logging.debug('getting workflow runs for repository', repo=repository.full_name, start=start, end=end, status=status, branch=branch)

    all:list[WorkflowRun] = []
    dates:list[str] = date_range_as_strings(start=start, end=end, inc=Increment.MONTH)
    logging.debug('date ranges', repo=repository.full_name, start=start, end=end, dates=dates)

    for ym in dates:
        date_range:str = f'{ym}..{ym}'   
        logging.info(f'[{repository.full_name}] (workflow_runs) getting workflow in range',  repo=repository.full_name, date_range=date_range)     
        runs:list[WorkflowRun] = __workflow_runs__(repository=repository, branch=branch, 
                                                   date_range=date_range, status=status)
        all += runs
    logging.info(f'[{repository.full_name}] (workflow_runs) found [{len(all)}] overall workflow_runs in range',  repo=repository.full_name, start=start, end=end, status=status, branch=branch)
    return all

def matching_workflow_runs(pattern:str, 
                           workflow_runs:list[WorkflowRun]) -> list[WorkflowRun]:
    """Reduce the list of workflow runs to those that match the pattern"""
    logging.debug('getting workflow runs matching pattern', pattern=pattern)
    matched:list[WorkflowRun] = []
    repo:str = None
    total:int = len(workflow_runs)
    for i, wf in enumerate(workflow_runs):
        if wf.repository is not None and repo is None:        
            repo = wf.repository.full_name
        pattern_match:bool = bool(re.search(pattern, wf.name.lower())) if pattern is not None else True
        flag:str = "✅" if pattern_match else "❌" 
        logging.debug(f'[{repo}] (workflow_runs) [{i}+1/{total}] workflow pattern matched {flag}', pattern=pattern, workflow_run=wf.id, workflow_name=wf.name)     
        if pattern_match:            
            matched.append(wf)
    logging.info(f'[{repo}] (workflow_runs) found [{len(matched)}] that match pattern', pattern=pattern)
    return matched 
