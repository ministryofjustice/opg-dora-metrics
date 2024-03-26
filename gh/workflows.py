import logging
from github.WorkflowRun import WorkflowRun
from github.WorkflowJob import WorkflowJob
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from timer.stopwatch import durations


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

        logging.debug(f"[workflow:{workflow.name}][job:{job.name}] duration: [{job_durations.get('seconds')}]")

    logging.info(f"[workflow:{workflow.name}] >> total duration: [{total_durations.get('seconds')}]")
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
