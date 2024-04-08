import re
from typing import Any, Callable
from datetime import date

from github import Github
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from github.WorkflowRun import WorkflowRun
from github.PullRequest import PullRequest

from converter.meta import attributes
from converter.convert import to, remapper
from log.logger import logging
from utils.decorator import timer

from utils.dates import between, year_month_list, weekdays_in_month, to_date
from utils.group import group, range_fill
from utils.total import totals
from utils.average import averages

from pprint import pp


class GithubRepository:
    """GithubRepository provides a series of methods that wrap and process calls using the github sdk.

    Main aim is to fetch metric values for a specific repository
    """
    g:Github = None
    slug:str = None
    r:Repository = None

    @timer
    def __init__(self, g:Github, slug:str) -> None:
        self.g = g
        self.slug = slug
        self.r = self._repo()
        logging.info('found repository', slug=slug)

    @timer
    def _repo(self) -> Repository:
        logging.info('calling github api to get repository')
        return self.g.get_repo(self.slug)

    @timer
    def name(self) -> str:
        """Use the repos full_name"""
        return self.r.full_name

    ############
    # Metrics
    ############

    @timer
    def deployment_frequency(self, start:date, end:date, branch:str='main', workflow_pattern:str = ' live'):
        """Measure the number of github action workflow runs (success and failures) between the date range specified
        as part of DORA style reporting.

        Allows the workflow pattern name to be passed to reduce the number of workflows to just path to live versions.
        Allows changing the release branch from the default of 'main', useful for older repository that may still be
        on 'master'

        If the repository is using an alternative deployment tool (jenkins, circleci etc) then uses merges into the
        specified branch as a proxy measurement.
        """
        data:list[dict] = self.workflow_runs(workflow_pattern, branch, start, end)
        if len(data) == 0:
            logging.warn('No workflow runs found, using proxy measure of pull requests')
            data = self.pull_requests(branch, start, end)


        grouped = self._groupby(data, start, end)
        totaled = self._totals(grouped, 'conclusion')
        averages = self._averages(totaled)

        return averages

    @timer
    def _averages(self, totals:dict[str, dict[str,Any]]) -> dict[str, dict[str,Any]]:
        """Append average information into the totals"""
        avgf = lambda month, value: ( round( value / weekdays_in_month( to_date(month) ), 2 ) )
        return averages(totals, avgf)

    @timer
    def _totals(self, data:dict[str, list[dict[str,Any]]], key:str) -> dict[str, dict[str,Any]]:
        """Create totals for each group with extra total count for each value of key"""
        return totals(data, key)

    @timer
    def _groupby(self, items:list[dict[str,Any]], start:date, end:date ) -> dict[str, list[dict[str,Any]]]:
        """Handle grouping a list of objects"""
        group_function = lambda x : x.get('date').strftime('%Y-%m')
        return range_fill(
            group(items, group_function),
            year_month_list(start, end)
        )


    ############
    # Pull Requests
    ############

    @timer
    def _get_pull_requests(self, branch:str, state:str = 'closed') -> list[PullRequest]:
        """Deals with the paginated list and returns a normal list so there is no futher rate limiting and allows for mocking of this result"""
        logging.info('calling github api for pull requests')
        prs:PaginatedList[PullRequest] = self.r.get_pulls(base=branch, state=state, sort='merged_at', direction='desc')
        pp(prs)
        all:list[PullRequest] = [pr for pr in prs]
        return all

    @timer
    def _parse_pull_requests(self, prs:list[PullRequest], branch:str, start:date, end:date) -> list[dict[str,Any]]:
        """Reduces all pr's down to those within date range - converts to list of dict"""
        found:list[dict[str,Any]] = []
        total:int = len(prs)
        pr:PullRequest = None
        for i, pr in enumerate(prs):
            # change state to conclusion to match workflow run name and change value to success
            item:dict[str,Any] = to(pr,
                                    remap=[
                                        remapper('merged_at', 'date'),
                                        remapper('state', 'status', lambda x: ('success'))
                                    ])

            if between(item.get('date'), start, end):
                logging.debug('within range ✅', repo=self.name(), i=f'{i}/{total}', pr=item.get('title'), branch=branch, date=item.get('date'))
                found.append(item)
            else:
                logging.debug('out of range ❌', repo=self.name(), i=f'{i}/{total}', pr=item.get('title'), branch=branch, date=item.get('date'))
        return found

    @timer
    def pull_requests(self, branch:str, start:date, end:date, state:str = 'closed') -> list[dict[str,Any]]:
        """Return a list of that have been reduce down to attributes from Keep data

        Calls _get_pull_requests to fetch all pull requests for the branch name, this may be many hundreds as the api
        has no date range limit
        Then call _parse_pull_requests with the result to reduce the set to those that are within the date range and
        in turn converts the matching pr.

        Parameters:

        branch (str):   Branch that the pull request was to merge into
        start (date):   Start of the date range to query for
        end (date):     End of the date range to query for
        state (str):    State of the pull request (default: closed)
        """
        logging.info('getting pull requests', repo=self.name(), branch=branch, start=start, end=end, state=state)
        prs:list[PullRequest] = self._get_pull_requests(branch, state)
        found:list[dict[str,Any]] = self._parse_pull_requests(prs, branch, start, end)
        return found

    ############
    # Workflows
    ############
    @timer
    def _get_workflow_runs(self, branch:str, date_range:str) -> list[WorkflowRun]:
        """Deals with the paginated list sand returns a normal list so there is no futher rate limiting etc"""
        logging.info('calling github api for workflow runs')
        runs:PaginatedList[WorkflowRun] = self.r.get_workflow_runs(branch=branch, created=date_range)
        all:list[WorkflowRun] = [run for run in runs]
        return all

    @timer
    def _parse_workflow_runs(self, runs:list[WorkflowRun], pattern:str, start: date, end:date) -> list[dict[str,Any]]:
        """Reduces all workflows down to those that match pattern and within date range - converts to list of dicts.

        Note: Only attributes whose name is within fields will be added
        """
        found:list[dict[str,Any]] = []
        for workflow in runs:
            if not between(workflow.created_at, start, end):
                logging.debug('outside of date range ❌', repo=self.name(), workflow=workflow.name, pattern=pattern, branch=workflow.head_branch, date=workflow.created_at)
            elif re.search(pattern, workflow.name.lower()):
                logging.debug('match ✅', repo=self.name(), workflow=workflow.name, pattern=pattern, branch=workflow.head_branch, date=workflow.created_at)
                item:dict[str,Any] = to(workflow,
                                        remap=[
                                            remapper('conclusion', 'status'),
                                            remapper('created_at', 'date'),
                                        ])
                found.append(item)
            else:
                logging.debug('no match ❌', repo=self.name(), workflow=workflow.name, pattern=pattern, branch=workflow.head_branch, date=workflow.created_at)
        return found

    @timer
    def workflow_runs(self, pattern:str, branch:str, start: date, end:date) -> list[dict[str,Any]]:
        """Return a list of dict objects that have been reduce down to attributes from Keep config

        Calls _get_workflow_runs to fetch pull workflow runs from for the branch and date range passed.
        Then call _parse_workflow_runs with the result to reduce the set to those that match the name pattern, which
        in turn converts the matching workflows into dict objects.

        Parameters:

        pattern (str):  Used to pattern match against the lower case version of workflow.name using re.search
        branch (str):   Branch that the workflow ran against
        start (date):   Start of the date range to query for
        end (date):     End of the date range to query for
        """
        logging.info('looking for workflow runs matching pattern', repo=self.name(), pattern=pattern, branch=branch, start=start, end=end)
        date_range:str = f'{start}..{end}'

        all:list[WorkflowRun] = self._get_workflow_runs(branch, date_range)
        found:list[dict[str,Any]] = self._parse_workflow_runs(all, pattern, start, end)

        logging.info('finished workflow runs', found=len(found), total=len(all), repo=self.name(), pattern=pattern, branch=branch, start=start, end=end)
        return found
