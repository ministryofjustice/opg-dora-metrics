import re
from datetime import date, datetime
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from app.dates.convert import to_datetime
from app.dates.between import between
from app.logger import logging
from app.decorator import timer

@timer
def pull_requests_in_range(repository:Repository,
                           start:date, end:date,
                           branch:str, state:str='closed') -> list[PullRequest]:
    """Return all the prs"""
    logging.debug(f'[{repository.full_name}] (pull_requests) getting all', repo=repository.full_name, branch=branch)
    lower:datetime = to_datetime(start)
    upper:datetime = to_datetime(end)
    remote_prs = repository.get_pulls(base=branch, state=state, sort='merged_at', direction='desc')
    total:int = remote_prs.totalCount

    prs:list[PullRequest] = []

    for pr in remote_prs:
        in_range = between(test=pr.merged_at, lower=lower, upper=upper)
        if in_range:
            prs.append(pr)
        # presume in date order, skip when we goet out of range
        elif pr.merged_at is not None and pr.merged_at < lower:
            logging.debug(f'[{repository.full_name}] (pull_requests) pr is older than range, skipping', repo=repository.full_name, branch=branch)
            break

    logging.info(f'[{repository.full_name}] (pull_requests) found {len(prs)}/{total} pull_requests in range', repo=repository.full_name, branch=branch)
    return prs


@timer
def merged_pull_requests(pull_requests:list[PullRequest]) -> list[PullRequest]:
    """Return a list of prs for the repo in the date range set"""
    logging.debug('getting merged pull requests')

    matched:list[PullRequest] = []
    total:int = len(pull_requests)
    i:int = 1

    for i, pr in enumerate(pull_requests):
        merged:bool = pr.merged

        merge_flag:str = "✅" if merged else "❌"
        logging.debug(f'(pull_requests) [{i+1}/{total}] pr is merged {merge_flag}', date=pr.merged_at)
        # attach to matched when its in range
        if merged:
            matched.append(pr)
        # i += 1

    logging.info(f'(pull_requests) found [{len(matched)}] merged prs that have been merged')
    return matched
