from typing import Any, TypeVar, Callable
from pprint import pp
from github.GithubObject import GithubObject
from github.Artifact import  Artifact
from github.WorkflowRun import  WorkflowRun
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.Team import Team
from app.data.local.github.base import DataMap
from app.log.logger import logging
from app.decorator import timer
G = TypeVar('G', bound=GithubObject)

################################################
# Map the attributes to either their values or
# a function to fetch the data we want
################################################
ArtifactAttributes:dict[str, Callable|None] = {
    'id': None,
    'name': None,
    'archive_download_url': None,
    'created_at': lambda x: x.created_at.isoformat(),
    'workflow_run_id': lambda x: x.workflow_run.id,
    'repository_id': lambda x: x.workflow_run.repository.id,
    'date': lambda x: x.created_at.isoformat(),
}
WorkflowRunAttributes:dict[str, Callable|None] = {
    'id': None,
    'name': None,
    'conclusion': None,
    'head_branch': None,
    'created_at': lambda x: x.created_at.isoformat(),
    'repository_full_name': lambda x: x.repository.full_name,
    'repository_id': lambda x: x.repository.id,
    'teams': lambda x: [t.slug for t in x.repository.get_teams()],
    'date': lambda x: x.created_at.isoformat(),
}
TeamAttributes:dict[str, Callable|None] = {
    'id': None,
    'name': None,
    'slug': None,
    'parent_id': lambda x:  x.parent.id,
}
PullRequestAttributes:dict[str, Callable|None] = {
    'id': None,
    'title': None,
    'state': None,
    'base': lambda x: x.base.ref,
    'number': None,
    'merged': None,
    'merged_at': lambda x: x.merged_at.isoformat(),
    'url': None,
    'repository_full_name': lambda x: x.base.repo.full_name,
    'repository_id': lambda x: x.base.repo.id,
    'teams': lambda x: [t.slug for t in x.base.repo.get_teams()],
    'date': lambda x: x.merged_at.isoformat(),
}
# split out some repo fields for ease in checking
RepositoryBaselineComplianceAttributes:dict[str, Callable|None] = {
    'default_branch_is_main': lambda r: r.default_branch == 'main',
    'default_branch_is_protected': lambda r: r.get_branch(r.default_branch).protected,
    'has_issues': None,
    'rules_enforced_for_admins': lambda r: r.get_branch(r.default_branch).get_admin_enforcement(),
    'requires_approval': lambda r: r.get_branch(r.default_branch).get_required_pull_request_reviews().required_approving_review_count > 0,
    'has_description': lambda r: len(r.description) > 0,
    'has_license': lambda r: len(r.get_license().license.name) > 0,
}
RepositoryExtendedComplianceAttributes:dict[str, Callable|None] = {
    'requires_code_owner_approval': lambda r: r.get_branch(r.default_branch).get_required_pull_request_reviews().require_code_owner_reviews,
    'vulnerability_alerts_enabled': lambda r: r.get_vulnerability_alert(),
    'has_readme': lambda r: len(r.get_contents('./README.md').content) > 0,
    'has_codeowners_in_github_dir': lambda r: len(r.get_contents('./.github/CODEOWNERS').content) > 0,
    'has_code_of_conduct': lambda r: len(r.get_contents('./CODE_OF_CONDUCT.md').content) > 0,
    'has_contributing_guide': lambda r: len(r.get_contents('./CONTRIBUTING.md').content) > 0,
}
RepositoryDetailedAttributes:dict[str, Callable|None] = {
    'archived':  None,
    'has_projects':  None,
    'has_pages':  None,
    'has_downloads':  None,
    'has_wiki':  None,
    'license_name': lambda r: r.get_license().license.name,
    'forks_count': None,
    'webhooks_count': lambda r: r.get_hooks().totalCount,
    'open_pull_request_count': lambda r: r.get_pulls(state='open', sort='created', base=r.default_branch).totalCount,
    'last_commit_date': lambda r: r.get_branch(r.default_branch).commit.commit.committer.date.isoformat(),
    'clone_traffic_count': lambda r: r.get_clones_traffic()['count'],
    'private': None,
}

RepositoryAttributes:dict[str, Callable|None] = {
    # core
    'id': None,
    'name': None,
    'full_name': None,
    'default_branch': None,
    'url':  None,
    'description': None,
}
RepositoryAttributes.update(RepositoryDetailedAttributes)
RepositoryAttributes.update(RepositoryBaselineComplianceAttributes)
RepositoryAttributes.update(RepositoryExtendedComplianceAttributes)
################################################
__map__: dict = {
    Artifact: ArtifactAttributes,
    WorkflowRun: WorkflowRunAttributes,
    Team: TeamAttributes,
    Repository: RepositoryAttributes,
    PullRequest: PullRequestAttributes,
}
################################################
#
################################################

@timer
def Local(source:G) -> dict[str, Any]:
    """Uses the attributes and type of the source to generate a dict of information we want"""
    assert isinstance(source, GithubObject)
    t = type(source)
    logging.debug('Localising details', type=t, source=source)

    if t not in __map__.keys():
        raise Exception(f'Type of source object is not supported: [{t}]')

    attrs:dict = __map__[t]
    mapped:dict = DataMap(source, attrs)
    # if its a report add some empty fields
    if t is Repository:
        mapped.update({'teams':[], 'workflow_runs':[], 'artifacts': [], 'pull_requests': []})
    elif t is WorkflowRun:
        mapped.update({'artifacts': []})
    return mapped
