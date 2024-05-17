import re
from datetime import date, datetime
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from app.utils.dates.convert import to_datetime
from app.utils.dates.between import between
from app.log.logger import logging
from app.decorator import timer

@timer
def __pull_requests__(repository:Repository, branch:str, state:str='closed') -> list[PullRequest]:
    """Return all the prs"""
    logging.debug(f'[{repository.full_name}] (pull_requests) getting all', repo=repository.full_name, branch=branch)
    prs:list[PullRequest] = [pr for pr in repository.get_pulls(base=branch, state=state, sort='merged_at', direction='desc')]
    logging.info(f'[{repository.full_name}] (pull_requests) found {len(prs)} pull_requests', repo=repository.full_name, branch=branch)
    return prs

@timer
def merged_pull_requests(repository:Repository, branch:str, start:date, end:date) -> list[PullRequest]:
    """Return a list of prs for the repo in the date range set"""    
    
    logging.debug('getting pull_requests in date range', repo=repository.full_name, start=start, end=end, branch=branch)
    all:list[PullRequest] = __pull_requests__(repository=repository, branch=branch, state='closed')
    matched:list[PullRequest] = []
    repo:str = repository.full_name
    total:int = len(all)

    lower:datetime = to_datetime(start)
    upper:datetime = to_datetime(end)
    last_date:datetime = None

    for i, pr in enumerate(all):        
        merged:bool = pr.merged        
        in_range = between(test=pr.merged_at, lower=lower, upper=upper)
        
        merge_flag:str = "✅" if merged else "❌" 
        range_flag:str = "✅" if in_range else "❌" 
        logging.debug(f'[{repo}] (pull_requests) [{i+1}/{total}] pr is merged {merge_flag} and in range {range_flag}', repo=repository.full_name, date=pr.merged_at, branch=branch, start=start, end=end)  
        # attach to matched when its in range
        if merged and in_range:
            matched.append(pr)
        # if the last_date is before start, then we can stop here as results are returned in date order
        if last_date is not None and last_date < lower:
            logging.info(f'[{repo}] (pull_requests) skipping remaining pull_requests', start=start, end=end)
            break
        last_date = pr.merged_at

    logging.info(f'[{repo}] (pull_requests) found [{len(matched)}] within date range', start=start, end=end)
    return matched
