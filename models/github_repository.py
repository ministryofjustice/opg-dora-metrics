import re
from typing import Any
from datetime import date

from github import Github
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from github.WorkflowRun import WorkflowRun
from github.PullRequest import PullRequest
from github.Team import Team

from converter.convert import to, remapper
from log.logger import logging
from utils.decorator import timer
from utils.dates import between, year_month_list, weekdays_in_month, to_date
from utils.group import group, range_fill
from utils.total import totals
from utils.average import averages

from pprint import pp


class _Standards:
    """Handle all the complance related methods and data gathering"""
    g:Github = None
    name:str = None
    r:Repository = None

    def __init__(self, g:Github, r:Repository, name) -> None:
        self.g = g
        self.r = r
        self.name = name

    @timer
    def _has_file(self, filepath:str) -> bool:
        """Check the file path exists and has content"""
        try:
            found = self.r.get_contents(filepath)
            return True
        except:
            return False
        return False

    @timer
    def compliant(self) -> dict[str, Any]:
        """Check the repo is compliant against base line and extended standards"""

        base:dict[str, Any] = self.baseline()
        extras:dict[str,Any] = self.extended()
        base.update(extras)
        base['_archived'] = self.r.archived

        # now add in stats to that
        base['__Last commit date'] = self.r.get_branch(self.r.default_branch).commit.commit.committer.date
        base['__Open pull requests'] = self.r.get_pulls(state='open', sort='created', base=self.r.default_branch).totalCount
        base['__Forks'] = self.r.forks_count
        try:
            base['__Clone traffic'] = self.r.get_clones_traffic()['count']
        except:
            base['__Clone traffic'] = 'N/A'

        return base

    @timer
    def baseline(self) -> dict[str, Any]:
        """Baseline standards that ops-eng also report on"""
        l, lname = self.has_license()
        base:dict[str,Any] = {
            '[B] Default branch is called main': self.default_branch_is_main(),
            '[B] Default branch is protected': self.default_branch_is_protected(),
            '[B] Issues are enabled': self.has_issues_enabled(),
            '[B] Rules enforced for admins': self.rules_enforced_for_admins(),
            '[B] Requires approval': self.approval_review_count_greater_than_zero(),
            '[B] Has a description': self.has_description(),
            '[B] Has a license': l,
        }
        overall:bool = True
        for k,v in base.items():
            if v is False:
                overall = False
        base['License type'] = lname
        base['_baseline'] = overall
        return base

    @timer
    def extended(self) -> dict[str, Any]:
        """Extra elements to check for"""
        extras:dict[str, Any] = {
            '[E] Requires code owner approval': self.requires_code_owner_reviews(),
            '[E] No Webhooks': (self.r.get_hooks().totalCount == 0),
            '[E] Vulnerability alerts are enabled': self.r.get_vulnerability_alert(),
            '[E] Code owners is in .github folder': self._has_file('./.github/CODEOWNERS'),
            '[E] Readme is present': self._has_file('./README.md'),
            '[E] Code of conduct is present': self._has_file('./CODE_OF_CONDUCT.md'),
            '[E] Contributing guide is present': self._has_file('./CONTRIBUTING.md'),
        }
        overall:bool = True
        for k,v in extras.items():
            if v is False:
                overall = False
        extras['_extended'] = overall
        return extras


    @timer
    def default_branch_is_main(self) -> bool:
        return self.r.default_branch == 'main'

    @timer
    def default_branch_is_protected(self) -> bool:
        return self.r.get_branch(self.r.default_branch).protected

    @timer
    def has_description(self) -> bool:
        return self.r.description != ''

    @timer
    def has_issues_enabled(self) -> bool:
        return self.r.has_issues

    @timer
    def approval_review_count_greater_than_zero(self) -> bool:
        count:int = 0
        try:
            branch = self.r.get_branch(self.r.default_branch)
            settings = branch.get_required_pull_request_reviews()
            count = settings.required_approving_review_count
        except Exception as e:
            count = 0
        return (count > 0)

    @timer
    def rules_enforced_for_admins(self) -> bool:
        status:bool = False
        try:
            branch = self.r.get_branch(self.r.default_branch)
            status = branch.get_admin_enforcement()
        except Exception as e:
            return False
        return status

    @timer
    def requires_code_owner_reviews(self) -> bool:
        status:bool = False
        try:
            branch = self.r.get_branch(self.r.default_branch)
            settings = branch.get_required_pull_request_reviews()
            status = settings.require_code_owner_reviews
        except Exception as e:
            return False
        return status

    @timer
    def has_license(self) -> tuple[bool, str]:
        status:bool = False
        name:str = ''
        try:
            license = self.r.get_license()
            name = license.license.name
            status = len(name) > 0
        except Exception as e:
            return False, ""
        return status, name


class _PullRequests:
    """Handle all things for pull requests"""
    g:Github = None
    r:Repository = None
    name:str = None

    def __init__(self, g:Github, r:Repository, name:str) -> None:
        self.g = g
        self.r = r
        self.name = name

    @timer
    def _get(self, branch:str, state:str = 'closed') -> list[PullRequest]:
        """Deals with the paginated list and returns a normal list so there is no futher rate limiting and allows for mocking of this result"""
        logging.debug('calling github api for pull requests', repo=self.name)
        prs:PaginatedList[PullRequest] = self.r.get_pulls(base=branch, state=state, sort='merged_at', direction='desc')
        all:list[PullRequest] = [pr for pr in prs]
        logging.info(f'found [{len(all)}] total pull requests', repo=self.name)
        return all

    @timer
    def _parse(self, prs:list[PullRequest], branch:str, start:date, end:date) -> list[dict[str,Any]]:
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
                logging.debug('within range ✅', repo=self.name, i=f'{i}/{total}', pr=item.get('title'), branch=branch, date=item.get('date'))
                found.append(item)
            else:
                logging.debug('out of range ❌', repo=self.name, i=f'{i}/{total}', pr=item.get('title'), branch=branch, date=item.get('date'))
        return found

    @timer
    def prs(self, branch:str, start:date, end:date, state:str = 'closed') -> list[dict[str,Any]]:
        """Return a list of that have been reduce down to attributes from Keep data

        Calls _get to fetch all pull requests for the branch name, this may be many hundreds as the api
        has no date range limit
        Then call _parse with the result to reduce the set to those that are within the date range and
        in turn converts the matching pr.

        Parameters:

        branch (str):   Branch that the pull request was to merge into
        start (date):   Start of the date range to query for
        end (date):     End of the date range to query for
        state (str):    State of the pull request (default: closed)
        """
        logging.debug('getting pull requests', repo=self.name, branch=branch, start=start, end=end, state=state)
        prs:list[PullRequest] = self._get_pull_requests(branch, state)
        found:list[dict[str,Any]] = self._parse_pull_requests(prs, branch, start, end)
        return found


class _Workflows:
    """Handle all things relating to workflows"""
    g:Github = None
    r:Repository = None
    name:str = None

    def __init__(self, g:Github, r:Repository, name:str) -> None:
        self.g = g
        self.r = r
        self.name = name

    @timer
    def _get(self, branch:str, start: date, end:date) -> list[WorkflowRun]:
        """Deals with the paginated list sand returns a normal list so there is no futher rate limiting etc"""
        logging.debug('calling github api for workflow runs', repo=self.name)

        all:list[WorkflowRun] = []
        months = year_month_list(start, end)
        for m in months:
            rloop:PaginatedList[WorkflowRun] = self.r.get_workflow_runs(branch=branch, created=f'{m}..{m}' )
            logging.debug(f'found [{rloop.totalCount}] workflows', repo=self.name, created=m, branch=branch)

            # warn about api max numbers
            if rloop.totalCount >= 1000:
                logging.error(f'error: hit max workflow results: [{rloop.totalCount}]', repo=self.name, created=m, branch=branch)
                for run in rloop:
                    logging.debug(f'workflow: {run.id} - {run.created_at} [{run.display_title}]')
                    all.append(run)
            else:
                for run in rloop:
                    all.append(run)

        logging.info(f'found [{len(all)}] total workflows', repo=self.name, start=start, end=end)
        return all

    @timer
    def _parse(self, runs:list[WorkflowRun], pattern:str, start: date, end:date) -> list[dict[str,Any]]:
        """Reduces all workflows down to those that match pattern and within date range - converts to list of dicts.

        Note: Only attributes whose name is within fields will be added
        """
        found:list[dict[str,Any]] = []
        for workflow in runs:
            if not between(workflow.created_at, start, end):
                logging.debug('outside of date range ❌', repo=self.name, workflow=workflow.name, pattern=pattern, branch=workflow.head_branch, date=workflow.created_at)
            elif re.search(pattern, workflow.name.lower()):
                logging.debug('match ✅', repo=self.name, workflow=workflow.name, pattern=pattern, branch=workflow.head_branch, date=workflow.created_at)
                item:dict[str,Any] = to(workflow,
                                        remap=[
                                            remapper('conclusion', 'status'),
                                            remapper('created_at', 'date'),
                                        ])
                found.append(item)
            else:
                logging.debug('no match ❌', repo=self.name, workflow=workflow.name, pattern=pattern, branch=workflow.head_branch, date=workflow.created_at)
        return found

    @timer
    def runs(self, pattern:str, branch:str, start: date, end:date) -> list[dict[str,Any]]:
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
        logging.debug('looking for workflow runs matching pattern', repo=self.name, pattern=pattern, branch=branch, start=start, end=end)
        # date_range:str = f'{start}..{end}'

        all:list[WorkflowRun] = self._get(branch, start, end)
        found:list[dict[str,Any]] = self._parse(all, pattern, start, end)

        logging.debug('finished workflow runs', found=len(found), total=len(all), repo=self.name, pattern=pattern, branch=branch, start=start, end=end)
        return found


class _Metrics:
    """Handles the metric calculations"""
    g:Github = None
    r:Repository = None
    name:str = None

    def __init__(self, g:Github, r:Repository, name:str) -> None:
        self.g = g
        self.r = r
        self.name = name

    @timer
    def averages(self, totals:dict[str, dict[str,Any]]) -> dict[str, dict[str,Any]]:
        """Append average information into the totals"""
        avgf = lambda month, value: ( round( value / weekdays_in_month( to_date(month) ), 2 ) )
        return averages(totals, avgf)

    @timer
    def totals(self, data:dict[str, list[dict[str,Any]]], key:str) -> dict[str, dict[str,Any]]:
        """Create totals for each group with extra total count for each value of key"""
        return totals(data, key)

    @timer
    def groupby(self, items:list[dict[str,Any]], start:date, end:date ) -> dict[str, list[dict[str,Any]]]:
        """Handle grouping a list of objects"""
        group_function = lambda x : x.get('date').strftime('%Y-%m')
        return range_fill(
            group(items, group_function),
            year_month_list(start, end)
        )


class GithubRepository:
    """GithubRepository provides a series of methods that wrap and process calls using the github sdk.

    Used for reports to fetch metrics, standards checking and similar
    """
    g:Github = None
    slug:str = None
    name:str = None
    r:Repository = None

    # setters
    _standards:_Standards = None
    _workflows:_Workflows = None
    _pr:_PullRequests = None
    _metrics:_Metrics = None

    @timer
    def __init__(self, g:Github, slug:str) -> None:
        self.g = g
        self.slug = slug
        self.r = self._repo()
        logging.debug('found repository', slug=slug)
        self.name = self.r.full_name

    @timer
    def _repo(self) -> Repository:
        logging.debug('calling github api to get repository')
        return self.g.get_repo(self.slug)

    @timer
    def standards(self) -> _Standards:
        if self._standards is None:
            self._standards = _Standards(self.g, self.r, self.name)
        return self._standards

    @timer
    def workflows(self) -> _Workflows:
        if self._workflows is None:
            self._workflows = _Workflows(self.g, self.r, self.name)
        return self._workflows

    @timer
    def pull_requests(self) -> _PullRequests:
        if self._pr is None:
            self._pr = _PullRequests(self.g, self.r, self.name)
        return self._pr

    @timer
    def metrics(self) -> _Metrics:
        if self._metrics is None:
            self._metrics = _Metrics(self.g, self.r, self.name)
        return self._metrics

    @timer
    def teams(self, parent:str = 'opg') -> list[Team]:
        """Fetch all teams for this repo"""
        all:list[Team] = []
        for t in self.r.get_teams():
            if t.parent is not None and t.parent.slug == parent:
                all.append(t)
        return all

    ###############
    # REPORTS
    ###############
    @timer
    def deployment_frequency(self, start:date, end:date, branch:str='main', workflow_pattern:str = ' live') -> dict[str, dict[str,Any]]:
        """Measure the number of github action workflow runs (success and failures) between the date range specified
        as part of DORA style reporting.

        Allows the workflow pattern name to be passed to reduce the number of workflows to just path to live versions.
        Allows changing the release branch from the default of 'main', useful for older repository that may still be
        on 'master'

        If the repository is using an alternative deployment tool (jenkins, circleci etc) then uses merges into the
        specified branch as a proxy measurement.
        """
        data:list[dict] = self.workflows().runs(workflow_pattern, branch, start, end)
        if len(data) == 0:
            logging.warn('No workflow runs found, using proxy measure of pull requests', repo=self.name)
            data = self.pull_requests().prs(branch, start, end)

        logging.info(f'found [{len(data)}] total df measures in range [{self.name}]', repo=self.name, start=start, end=end)

        grouped:dict[str, list[dict[str,Any]]] = self.metrics().groupby(data, start, end)
        logging.debug('grouped results', grouped=grouped, repo=self.name)

        totaled:dict[str, dict[str,Any]] = self.metrics().totals(grouped, 'status')
        logging.debug('totaled results', totaled=totaled, repo=self.name)

        averages:dict[str, dict[str,Any]] = self.metrics().averages(totaled)
        logging.debug('averages results', averages=averages, repo=self.name)

        return averages

    @timer
    def standards_compliant(self) -> dict[str, Any]:
        """Fetch a dict determining a series of compliance checks have been met"""
        return self.standards().compliant()
