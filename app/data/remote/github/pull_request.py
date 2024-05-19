import re
from datetime import date, datetime
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from app.dates.convert import to_datetime
from app.dates.between import between
from app.log.logger import logging
from app.decorator import timer

@timer
def __pull_requests_in_range__(repository:Repository,
                               lower:datetime, upper:datetime,
                               branch:str, state:str='closed') -> list[PullRequest]:
    """Return all the prs"""
    logging.debug(f'[{repository.full_name}] (pull_requests) getting all', repo=repository.full_name, branch=branch)
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
def merged_pull_requests(repository:Repository, branch:str, start:date, end:date) -> list[PullRequest]:
    """Return a list of prs for the repo in the date range set"""
    logging.debug('getting pull_requests in date range', repo=repository.full_name, start=start, end=end, branch=branch)

    lower:datetime = to_datetime(start)
    upper:datetime = to_datetime(end)


    all:list[PullRequest] = __pull_requests_in_range__(repository=repository,
                                              branch=branch,
                                              lower=lower,
                                              upper=upper,
                                              state='closed')
    matched:list[PullRequest] = []
    repo:str = repository.full_name
    total:int = len(all)

    for i, pr in enumerate(all):
        merged:bool = pr.merged is True
        in_range = between(test=pr.merged_at, lower=lower, upper=upper)

        merge_flag:str = "✅" if merged else "❌"
        range_flag:str = "✅" if in_range else "❌"
        logging.debug(f'[{repo}] (pull_requests) [{i+1}/{total}] pr is merged {merge_flag} and in range {range_flag}', repo=repository.full_name, date=pr.merged_at, branch=branch, start=start, end=end)
        # attach to matched when its in range
        if merged and in_range:
            matched.append(pr)

    logging.info(f'[{repo}] (pull_requests) found [{len(matched)}] merged prs within date range', start=start, end=end)
    return matched
