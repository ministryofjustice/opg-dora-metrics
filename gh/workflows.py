import logging
import re
from github.WorkflowRun import WorkflowRun
from github.WorkflowJob import WorkflowJob
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from timer.stopwatch import durations


def workflow_runs_by_name_fuzzy(workflow_pattern:str, r:Repository, date_range:str = None, branch:str = "main") -> list[WorkflowRun]:
    """Fetch the workflows for repository via workflow_runs and then filter that set based on the regex match against workflow_pattern

    Parameters:
    workflow_pattern (str): A regex pattern (used in re.match) to use to match against workflow name. When matched, the workflow will be included
    r (Repository): The git repository to pull workflow runs from
    date_range (str): A date range string in the format of YYYY-MM-dd..YYYY-MM-dd
    branch (str): branch name to look for workflows being run against (default: main)

    Return:
    list (WorkflowRun): The set of WorkflowRun's that matched the pattern, or an empty list

    """

    logging.info(f"[repo:{r.name}] looking for workflow runs for [{workflow_pattern}] during [{date_range}] on [{branch}]")
    workflows:list[WorkflowRun] = workflow_runs(r, date_range, branch, None)
    filtered:list[WorkflowRun] = []

    logging.info(f"[repo:{r.name}] filtering workflow runs on name matching [{workflow_pattern}]")
    for workflow in workflows:
        if re.search(workflow_pattern, workflow.name.lower() ):
            logging.debug(f"[repo:{r.name}] [workflow:{workflow.name}] matches [{workflow_pattern}]")
            filtered.append(workflow)
        else:
            logging.debug(f"[repo:{r.name}] [workflow:{workflow.name}] does not match [{workflow_pattern}]")

    return filtered

def workflow_runs_by_name(workflow_name:str, r:Repository, date_range:str = None, branch:str = "main") -> list[WorkflowRun]:
    """Fetch the workflows for repository via workflow_runs and then filter that set based on the workflow_name match

    Parameters:
    workflow_name (str): Exact matching name for the workflow runs to return
    r (Repository): The git repository to pull workflow runs from
    date_range (str): A date range string in the format of YYYY-MM-dd..YYYY-MM-dd
    branch (str): branch name to look for workflows being run against (default: main)

    Return:
    list (WorkflowRun): The set of WorkflowRun's that matched the pattern, or an empty list

    """

    logging.info(f"[repo:{r.name}] looking for workflow runs for [{workflow_name}] during [{date_range}] on [{branch}]")
    workflows:list[WorkflowRun] = workflow_runs(r, date_range, branch, None)
    filtered:list[WorkflowRun] = []

    logging.info(f"[repo:{r.name}] filtering workflow runs on name matching [{workflow_name}]")
    for workflow in workflows:
        if workflow.name.lower() == workflow_name.lower():
            logging.debug(f"[repo:{r.name}] [workflow:{workflow.name}] matches [{workflow_name}]")
            filtered.append(workflow)
        else:
            logging.debug(f"[repo:{r.name}] [workflow:{workflow.name}] does not match [{workflow_name}]")

    return filtered

def workflow_runs(r:Repository, date_range:str, branch:str = "main" , status:str = None) -> list[WorkflowRun]:
    """Fetch workflow runs for the repository - add filters based on the other params passed in

    Parameters:
    r (Repository): The git repository to pull workflow runs from
    date_range (str): A date range string in the format of YYYY-MM-dd..YYYY-MM-dd
    branch (str): branch name to look for workflows being run against (default: main)
    status (str): The resulting status of the workflow to filter by (default: None)

    Return:
    list (WorkflowRun): The set of WorkflowRun's that matched the pattern, or an empty list
    """

    logging.info(f"[repo:{r.name}] looking for workflow runs during [{date_range}] on [{branch}]")
    # status in the lib can not be None, so use an if for that
    workflows:PaginatedList[WorkflowRun] = []
    if status is not None:
        workflows = r.get_workflow_runs(branch=branch, created=date_range, status=status)
    else:
        workflows = r.get_workflow_runs(branch=branch, created=date_range)

    found:list[WorkflowRun] = []

    for workflow in workflows:
        logging.debug(f"[repo:{r.name}] [workflow:{workflow.name}] [date:{workflow.created_at}]")
        found.append(workflow)
    return found


def workflow_total_durations(r:Repository, workflow_id:int) -> dict:
    """Returns total duration of this workflow by adding the duration of each job within this workflow.

    Parameters:
    r (Repository): Repository object to fetch workflow from
    workflow_id (int): The id of the workflow to use

    Returns:
    dict (str: float): total durations in various units of time
    """
    workflow:WorkflowRun = r.get_workflow_run(workflow_id)
    jobs:PaginatedList[WorkflowJob] = workflow.jobs()
    total_durations:dict = {}

    for job in jobs:
        job_durations = durations(job.started_at.isoformat(), job.completed_at.isoformat())
        # sum together values
        for k,v in job_durations.items():
            total_durations[k] = total_durations.get(k, 0.0) + v

        logging.debug(f"[repo:{r.name}] [workflow:{workflow.name}] [job:{job.name}] duration: [{job_durations.get('seconds')}]")

    logging.info(f"[repo:{r.name}] [workflow:{workflow.name}] >> total duration: [{total_durations.get('seconds')}]")
    return total_durations

def workflow_total_duration(r:Repository, workflow_id:int) -> int:
    """Retuns how long workflow took to complete (via sum of job execution time) in rounded seconds.

    Parameters:
    r (Repository): Repository object to fetch workflow from
    workflow_id (int): The id of the workflow to use

    Returns:
    int: total durations in seconds
    """
    total_durations:dict = workflow_total_durations(r, workflow_id)
    return round(total_durations.get('seconds', 0))
