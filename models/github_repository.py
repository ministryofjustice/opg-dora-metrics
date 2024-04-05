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
from models.keep import attrs
from log.logger import logging
from utils.decorator import timer
from utils.dates import between
from pprint import pp
from enum import Enum




class KeepWorkflowRunFields(Enum):
    Id = 'id'
    Name = 'name'
    CreatedAt = 'created_at'
    Conclusion = 'conclusion'

    @classmethod
    def strings(cls) -> list[str]:
        return [e.value for e in cls]

class KeepPullRequestFields(Enum):
    Id = 'id'
    Title = 'title'
    MergedAt = 'merged_at'
    State = 'state'

    @classmethod
    def strings(cls) -> list[str]:
        return [e.value for e in cls]


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
        workflow_runs:list[Item] = self.workflow_runs(workflow_pattern, branch, start, end)
        pp(workflow_runs)


    ############
    # Pull Requests
    ############

    @timer
    def _get_pull_requests(self, branch:str, state:str = 'closed') -> list[PullRequest]:
        """Deals with the paginated list and returns a normal list so there is no futher rate limiting and allows for mocking of this result"""
        logging.info('calling github api for pull requests')
        prs:PaginatedList[PullRequest] = self.r.get_pulls(base=branch, state=state, sort='merged_at', direction='desc')
        all:list[PullRequest] = [pr for pr in prs]
        return all

    @timer
    def _parse_pull_requests(self, prs:list[PullRequest], fields:list[str], branch:str, start:date, end:date) -> list[Item]:
        """Reduces all pr's down to those within date range - converts to list of Item"""
        found:list[Item] = []
        total:int = len(prs)
        pr:PullRequest = None
        for i, pr in enumerate(prs):
            item:Item = Item(data=pr, attrs_to_use=fields)
            item.rename('merged_at', 'date')
            if between(item.date, start, end):
                logging.debug('within range ✅', repo=self.name(), i=f'{i}/{total}', pr=item.title, branch=branch, date=item.date)
                found.append(item)
            else:
                logging.debug('out of range ❌', repo=self.name(), i=f'{i}/{total}', pr=item.title, branch=branch, date=item.date)
        return found

    @timer
    def pull_requests(self, branch:str, start:date, end:date, state:str = 'closed') -> list[Item]:
        """Return a list of Item objects that have been reduce down to attributes from Keep data

        Calls _get_pull_requests to fetch all pull requests for the branch name, this may be many hundreds as the api
        has no date range limit
        Then call _parse_pull_requests with the result to reduce the set to those that are within the date range and
        in turn converts the matching pr's into Item objects.

        Parameters:

        branch (str):   Branch that the pull request was to merge into
        start (date):   Start of the date range to query for
        end (date):     End of the date range to query for
        state (str):    State of the pull request (default: closed)
        """
        logging.info('getting pull requests', repo=self.name(), branch=branch, start=start, end=end, state=state)

        fields:list[str] = attrs(PullRequest)
        prs:list[PullRequest] = self._pull_requests(branch, state)
        found:list[Item] = self._parse_pull_requests(prs, fields, branch, start, end)
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
    def _parse_workflow_runs(self, runs:list[WorkflowRun], fields:list[str], pattern:str, start: date, end:date) -> list[Item]:
        """Reduces all workflows down to those that match pattern and within date range - converts to list of Item.

        Note: Only attributes whose name is within fields will be added to the Item object
        """
        found:list[Item] = []
        for workflow in runs:
            if not between(workflow.created_at, start, end):
                logging.debug('outside of date range ❌', repo=self.name(), workflow=workflow.name, pattern=pattern, branch=workflow.head_branch, date=workflow.created_at)
            elif re.search(pattern, workflow.name.lower()):
                logging.debug('match ✅', repo=self.name(), workflow=workflow.name, pattern=pattern, branch=workflow.head_branch, date=workflow.created_at)
                item:Item = Item(data=workflow, attrs_to_use=fields)
                # use the reduced version and standardise date field to be 'date'
                item.rename('created_at', 'date')
                found.append(item)
            else:
                logging.debug('no match ❌', repo=self.name(), workflow=workflow.name, pattern=pattern, branch=workflow.head_branch, date=workflow.created_at)
        return found

    @timer
    def workflow_runs(self, pattern:str, branch:str, start: date, end:date) -> list[Item]:
        """Return a list of Item objects that have been reduce down to attributes from Keep config

        Calls _get_workflow_runs to fetch pull workflow runs from for the branch and date range passed.
        Then call _parse_workflow_runs with the result to reduce the set to those that match the name pattern, which
        in turn converts the matching workflows into Item objects.

        Parameters:

        pattern (str):  Used to pattern match against the lower case version of workflow.name using re.search
        branch (str):   Branch that the workflow ran against
        start (date):   Start of the date range to query for
        end (date):     End of the date range to query for
        """
        logging.info('looking for workflow runs matching pattern', repo=self.name(), pattern=pattern, branch=branch, start=start, end=end)

        fields: list[str] = attrs(WorkflowRun)
        date_range:str = f'{start}..{end}'

        all:list[WorkflowRun] = self._get_workflow_runs(branch, date_range)
        found:list[Item] = self._parse_workflow_runs(all, fields, pattern, start, end)

        logging.info('finished workflow runs', found=len(found), total=len(all), repo=self.name(), pattern=pattern, branch=branch, start=start, end=end)
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
