import json
import re
from typing import Tuple
from datetime import date, datetime

from github import Github
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from github.WorkflowRun import WorkflowRun
from github.PullRequest import PullRequest

from models.item import Item
from log.logger import logging
from utils.decorator import timer
from utils.dates import between
from pprint import pp



class GithubRepository:
    """"""

    g:Github = None
    slug:str = None
    r:Repository = None

    @timer
    def __init__(self, g:Github, slug:str) -> None:
        """"""
        self.g = g
        self.slug = slug
        self.r = self._repo()
        logging.info('found repository', slug=slug)

    @timer
    def _repo(self) -> Repository:
        return self.g.get_repo(self.slug)

    @timer
    def name(self) -> str:
        """Use the repos full_name"""
        return self.r.full_name


    ############
    # Pull Requests
    ############

    @timer
    def _pull_requests(self, branch:str, start:date, end:date, state:str = 'closed') -> list[PullRequest]:
        """Deals with the paginated list sand returns a normal list so there is no futher rate limiting and allows for mocking of this result"""
        prs:PaginatedList[PullRequest] = self.r.get_pulls(base=branch, state=state, sort='merged_at', direction='desc')
        all:list[PullRequest] = [pr for pr in prs]
        return all

    @timer
    def pull_requests(self, branch:str, start:date, end:date, state:str = 'closed') -> list[Item]:
        """Fetch the pull requests that were merted between the start and end date passed.

        """
        logging.info('getting pull requests', repo=self.name(), branch=branch, start=start, end=end, state=state)

        fields:list[str] = ['title', 'merged_at', 'state']
        prs:list[PullRequest] = self._pull_requests(branch, start, end, state)
        all:list[Item] = []

        total:int = len(prs)
        pr:PullRequest = None
        for i, pr in enumerate(prs):
            item:Item = Item(data=pr, attrs_to_use=fields)
            item.rename('merged_at', 'date')
            if between(item.date, start, end):
                logging.debug('within range ✅', repo=self.name(), i=f'{i}/{total}', pr=item.title, branch=branch, date=item.date)
                all.append(item)
            else:
                logging.debug('out of range ❌', repo=self.name(), i=f'{i}/{total}', pr=item.title, branch=branch, date=item.date)
        return all

    ############
    # Workflows
    ############
    @timer
    def _workflow_runs(self, branch:str, date_range:str) -> list[WorkflowRun]:
        """Deals with the paginated list sand returns a normal list so there is no futher rate limiting etc"""
        runs:PaginatedList[WorkflowRun] = self.r.get_workflow_runs(branch=branch, created=date_range)
        all: list[WorkflowRun] = [run for run in runs]


        return all

    @timer
    def workflow_runs(self, pattern:str, branch:str, start: date, end:date) -> list[Item]:
        """Return a list of Simple objects using only ['name', 'conclusion', 'date']

        Iterates over the result from repository.get_workflow_runs() and only returns those values
        that match the string pattern passed (using re.search).

        Parameters:

        pattern (str):  Used to pattern match against the lower case version of workflow.name using re.search
        branch (str):   Branch that the workflow ran against
        start (date):   Start of the date range to query for
        end (date):     End of the date range to query for
        """
        logging.info('looking for workflow runs matching pattern', repo=self.name(), pattern=pattern, branch=branch, start=start, end=end)

        fields: list[str] = ['name', 'conclusion', 'created_at']
        found:list[Item] = []
        date_range:str = f'{start}..{end}'
        # fetch all
        all:list[WorkflowRun] = self._workflow_runs(branch, date_range)
        for workflow in all:
            if re.search(pattern, workflow.name.lower()):
                logging.debug('match ✅', repo=self.name(), workflow=workflow.name, pattern=pattern, branch=branch, start=start, end=end)
                item:Item = Item(data=workflow, attrs_to_use=fields)
                # use the reduced version and standardise date field to be 'date'
                item.rename('created_at', 'date')
                found.append(item)
            else:
                logging.debug('no match ❌', repo=self.name(), workflow=workflow.name, pattern=pattern, branch=branch, start=start, end=end)

        logging.info('finished workflow runs', found=len(found), repo=self.name(), pattern=pattern, branch=branch, start=start, end=end)
        return found

    ##### Main metrics #####

    # def deployment_frequency(
    #         self,
    #         branch:str,
    #         start:date,
    #         end:date,
    #         path_to_live_pattern:str = " live"
    # ):
    #     """"""

    #     runs:list[Simple] = self.workflow_runs(path_to_live_pattern, branch, start, end)
    #     # no runs found, use pull requests merges as proxy measure
    #     if len(runs) == 0:
    #         logging.warning(f"[{self.name()}] [branch:{branch}] [workflow:{path_to_live_pattern}] not found, using merge counter as proxy")
    #         runs = self.pull_requests(branch, start, end)

    #     aggregated:dict[str, Simple] = self.aggregated_by_date(runs, start, end)

    # ##### Pull request / merge related #####

    # def pull_requests(
    #         self,
    #         branch:str,
    #         start:date,
    #         end:date,
    #         state:str = 'closed') -> tuple[int, list[Simple], list[Simple]]:
    #     """Fetch the pull requests that were merted between the start and end date passed.

    #     """
    #     logging.info(f"[{self.name()}] pull_requests between [{start}..{end}] for [{branch}] in state [{state}]")
    #     fields:list[str] = ['title', 'merged_at', 'state']

    #     prs:PaginatedList[PullRequest] = self.r.get_pulls(base=branch, state=state, sort='merged_at', direction='desc')
    #     all:list[Simple] = []
    #     in_range: list[Simple] = []

    #     total:int = prs.totalCount
    #     pr:PullRequest = None
    #     for i, pr in enumerate(prs):
    #         s:Simple = Simple.instance(pr, fields)
    #         s.set('date', s.get('merged_at'))
    #         del s.merged_at

    #         all.append(s)
    #         if between(start, end):
    #             logging.debug(f"[{self.name()}] [{i+1}/{total}] PR for [{branch}]@[{pr.merged_at}] in range ✅")
    #             in_range.append(pr)
    #         else:
    #             logging.debug(f"[{self.name()}] [{i+1}/{total}] PR for [{branch}]@[{pr.merged_at}] not in range ❌")
    #     return total, in_range, all


    # ##### Workflow frequency related #####

    # def aggregated_by_date(self, runs:list[Simple], start:date, end:date) -> dict[str, Simple]:
    #     """Return a dict of workflow run counters grouped by YYYY-MM of the created_at date.

    #     Creates a list of valid months (YYYY-MM) between start & end values and generates an initial empty
    #     counters for each

    #     Then iterates over the runs passed and creates an aggregated counter for each month based on
    #     the workflow conclusion

    #     Parameters:

    #     runs (list):    Set of Simple that we want to aggregate into months
    #     start (date):   Start of the date range
    #     end (date):     End of the date range

    #     """
    #     logging.info(f"[{self.name()}] aggregated_workflow_runs between [{start}..{end}] for runs passed")


    #     keys = year_month_list(start, end)
    #     # pre-populate the list
    #     aggregated:dict[str, dict] = {year_month: {} for year_month in keys}
    #     func = lambda x : x.get('date').strftime('%Y-%m')
    #     # group by a field, and setup totals
    #     collection = Collection(runs)
    #     totals = collection.totals('conclusion', func)
    #     # limit to just known months
    #     aggregated = {k:v for k,v in totals.items() if k in keys}
    #     return aggregated


    # def workflow_runs(self, pattern:str, branch:str, start: date, end:date) -> list[Simple]:
    #     """Return a list of Simple objects using only ['name', 'conclusion', 'date']

    #     Iterates over the result from repository.get_workflow_runs() and only returns those values
    #     that match the string pattern passed (using re.search).

    #     Parameters:

    #     pattern (str):  Used to pattern match against the lower case version of workflow.name using re.search
    #     branch (str):   Branch that the workflow ran against
    #     start (date):   Start of the date range to query for
    #     end (date):     End of the date range to query for
    #     """
    #     logging.info(f"[{self.name()}] workflow_runs matching [{pattern}] on [{branch}] between [{start}..{end}]")
    #     fields: list[str] = ['name', 'conclusion', 'created_at']
    #     found:list[Simple] = []
    #     date_range:str = f'{start}..{end}'
    #     # fetch all
    #     all:PaginatedList[WorkflowRun] = self.r.get_workflow_runs(branch=branch, created=date_range)
    #     for workflow in all:
    #         if re.search(pattern, workflow.name.lower()):
    #             logging.debug(f"[{self.name()}] [workflow:{workflow.name}] matches [{pattern}] ✅")
    #             # use the reduced version and standardise date field to be 'date'
    #             s:Simple = Simple.instance(workflow, fields)
    #             s.set('date', s.get('created_at'))
    #             del s.created_at
    #             found.append(s)
    #         else:
    #             logging.debug(f"[{self.name()}] [workflow:{workflow.name}] does not match [{pattern}] ❌")

    #     logging.info(f"[{self.name()}] found [{len(found)}] workflow_runs matching [{pattern}] on [{branch}] between [{start}..{end}]")
    #     return found
