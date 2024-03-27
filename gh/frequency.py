from github.WorkflowRun import WorkflowRun
from github.Repository import Repository
from datetime import date
from gh.workflows import workflow_runs_by_name_fuzzy
from pprint import pp
import logging
# known status options
status_options:list[str] = ['queued', 'in_progress', 'completed', 'success', 'failure', 'neutral', 'cancelled', 'skipped', 'timed_out', 'action_required']

def year_month_range(start:date, end:date) -> dict:
    """Generate a dict of dicts with YYYY-mm keys, each of which have a dict with keys from status_options and a count set to 0"""
    d:dict = {}
    logging.debug(f"Generating dict between [{start}] and [{end}]")
    for y in range (start.year, end.year+1):
        for m in range (start.month, end.month):
            k = f'{y}-{m :02d}'
            d[k] = dict((key, 0) for key in status_options)
    return d


def workflow_runs_by_month_fuzzy(workflow_pattern:str, r:Repository, start:date, end:date, branch:str = "main", status:str = None) -> dict|None:
    """Count all workflows for the workflow pattern and repository (that match criteria) between the selected dates and group them by conclusion (failure / success etc).

    Parameters:
    workflow_name (str):    Exact matching name for the workflow runs to return
    r (Repository):         The git repository to pull workflow runs from
    start (date):           Start of date range
    end (date):             End of date range
    branch (str):           The branch name to look for workflows being run against (default: main)
    status (str):           The resulting status of the workflow to filter by (default: None)

    Return:
    dict (str :dict)        Return a dict with top level keys YYYY-mm, each then contain status options with counters for each
    """

    date_range:str = f'{start}..{end}'
    logging.info(f"[{r.full_name}] counting workflow runs by month [{workflow_pattern}] during [{date_range}] on [{branch}] [status:{status}]")
    runs:list[WorkflowRun] = workflow_runs_by_name_fuzzy(workflow_pattern, r, date_range, branch, status)
    if len(runs) == 0:
        return None

    result:dict = year_month_range(start, end)
    for run in runs:
        d = run.created_at.date()
        key = f'{d.year}-{d.month :02d}'
        if key not in result:
            result[key] = dict((k, 0) for k in status_options)

        result[key][run.conclusion] = result[key][run.conclusion] + 1

    return result
