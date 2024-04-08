import os
from typing import Any
from datetime import date
from github import Github

from models.github_repository import GithubRepository
from utils.decorator import timer
from utils.dates import weekdays_in_month, to_date
from log.logger import logging

from pprint import pp

@timer
def deployment_frequency( repositories:list[dict[str,str]], start:date, end:date, g:Github) -> dict[str, dict[str, dict[str,Any]]]:
    """Fetch aggregated default information for all repositories passed"""
    logging.info('deployment frequency data', repository_config=repositories)

    # all the freq info
    all:dict[str, dict[str, Any]] = {}
    # stat items
    repository_names:list[str] = []
    weekdays:dict[str, int] = {}

    for conf in repositories:
        logging.debug('repository config', conf=conf)

        repo = GithubRepository(g, conf.get('repo'))
        repository_names.append(repo.name())
        logging.debug('repository name', name=repo.name())

        df:dict[str, dict[str, Any]] = repo.deployment_frequency(start, end, conf.get('branch'), conf.get('workflow') )
        # merge together
        for key,values in df.items():
            weekdays[key] = weekdays_in_month( to_date(key) )
            # set default
            if key not in all:
                all[key] = {}
            # merge in values
            for k, v in values.items():
                all[key][k] = all[key].get(k, 0) + v

    response:dict[str, dict[str, dict[str,Any]]] = {
        'meta': {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'repositories': repository_names,
            'weekdays': weekdays,
        },
        'result': all
    }
    pp(response)
    logging.info('deployment frequencies', result=response)

    return response
