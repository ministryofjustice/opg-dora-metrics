import logging
import re
from typing import Tuple
from datetime import date, datetime

from github import Github
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from github.WorkflowRun import WorkflowRun
from github.PullRequest import PullRequest

from models.aggregate import GroupBy, Totals
from models.simple import Simple
from utils.dates import year_month_list, weekdays_in_month, between

from pprint import pp



class GithubRepository:
    """"""

    g:Github = None
    r:Repository = None

    def __init__(self, g:Github, slug:str) -> None:
        """"""
        logging.debug(f"[{slug}] GithubRepository init")
        self.g = g
        self.r = g.get_repo(slug)

    def name(self) -> str:
        """Use the repos full_name"""
        return self.r.full_name


    ##### Pull request / merge related #####


    def pull_requests(
            self,
            branch:str,
            start:date,
            end:date,
            state:str = 'closed') -> tuple[int, list[Simple], list[Simple]]:
        """Fetch the pull requests that were merted between the start and end date passed.

        """
        logging.info(f"[{self.name()}] pull_requests between [{start}..{end}] for [{branch}] in state [{state}]")
        fields:list[str] = ['title', 'merged_at', 'state']

        prs:PaginatedList[PullRequest] = self.r.get_pulls(base=branch, state=state, sort='merged_at', direction='desc')
        all:list[Simple] = []
        in_range: list[Simple] = []

        total:int = prs.totalCount
        pr:PullRequest = None
        for i, pr in enumerate(prs):
            all.append(Simple.instance(pr, fields))
            if between(start, end):
                logging.debug(f"[{self.name()}] [{i+1}/{total}] PR for [{branch}]@[{pr.merged_at}] in range ✅")
                in_range.append(pr)
            else:
                logging.debug(f"[{self.name()}] [{i+1}/{total}] PR for [{branch}]@[{pr.merged_at}] not in range ❌")
        return total, in_range, all


    ##### Workflow frequency related #####

    def aggregated_workflow_runs(self, runs:list[Simple], start:date, end:date) -> dict[str, Simple]:
        """Return a dict of workflow run counters grouped by YYYY-MM of the created_at date.

        Creates a list of valid months (YYYY-MM) between start & end values and generates an initial empty
        counters for each

        Then iterates over the runs passed and creates an aggregated counter for each month based on
        the workflow conclusion

        Adds averages for each month

        Parameters:

        runs (list):    Set of Simple that we want to aggregate into months
        start (date):   Start of the date range
        end (date):     End of the date range

        """
        logging.info(f"[{self.name()}] aggregated_workflow_runs between [{start}..{end}] for runs passed")


        keys = year_month_list(start, end)
        # pre-populate the list
        aggregated:dict[str, dict] = {year_month: {} for year_month in keys}
        gFunc = lambda x : x.get('created_at').strftime('%Y-%m')
        # group by a field, and setup totals
        grouped:dict[str, list[Simple]] = GroupBy('conclusion', runs, groupByFunc=gFunc )
        totals:dict[str, Simple] = Totals('conclusion', grouped)

        for ym in keys:
            aggregated[ym] = totals.get(ym)

        return aggregated


    def workflow_runs(self, pattern:str, branch:str, start: date, end:date) -> list[Simple]:
        """Return a list of Simple objects using only ['name', 'conclusion', 'created_at']

        Iterates over the result from repository.get_workflow_runs() and only returns those values
        that match the string pattern passed (using re.search).

        Parameters:

        pattern (str):  Used to pattern match against the lower case version of workflow.name using re.search
        branch (str):   Branch that the workflow ran against
        start (date):   Start of the date range to query for
        end (date):     End of the date range to query for
        """
        logging.info(f"[{self.name()}] workflow_runs matching [{pattern}] on [{branch}] between [{start}..{end}]")
        fields: list[str] = ['name', 'conclusion', 'created_at']
        found:list[Simple] = []
        date_range:str = f'{start}..{end}'
        # fetch all
        all:PaginatedList[WorkflowRun] = self.r.get_workflow_runs(branch=branch, created=date_range)
        for workflow in all:
            if re.search(pattern, workflow.name.lower()):
                logging.debug(f"[{self.name()}] [workflow:{workflow.name}] matches [{pattern}] ✅")
                # use the reduced version
                found.append( Simple.instance(workflow, fields) )
            else:
                logging.debug(f"[{self.name()}] [workflow:{workflow.name}] does not match [{pattern}] ❌")
        return found
