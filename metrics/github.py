import os
from typing import Any
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta
from github import Github
from github.Team import Team

from models.github_repository import GithubRepository
from utils.decorator import timer
from utils.dates import weekdays_in_month, to_date, year_month_list, human_duration
from log.logger import logging

from pprint import pp


@timer
def standards_compliance(repositories:list[str], g:Github) -> dict[str, dict[str, dict[str,Any]]]:
    """Fetch stanards compliance checks for each repository passed"""
    logging.debug('standards compliance data', repositories=repositories)
    start_time:datetime = datetime.now(timezone.utc)

    compliance:dict[str, dict[str,Any]] = {}
    l:int = len(repositories)
    for i, slug in enumerate(repositories):
        logging.debug('getting standards_compliance for repo', repository_name=slug)
        repo = GithubRepository(g, slug)
        comp:dict[str,Any] = repo.standards_compliant()
        comp['_name'] = repo.name.replace('ministryofjustice/', '')
        compliance[repo.name] = comp
        logging.info(f'[{i+1}/{l}] standards_compliant for repo [{repo.name}]', repo=repo.name, compliance=comp)

    end_time:datetime = datetime.now(timezone.utc)
    duration = human_duration(start_time, end_time)

    response:dict[str, dict[str, dict[str,Any]]] = {
        'meta': {
            'repositories': repositories,
            'execution_time': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'duration': duration,
            }
        },
        'compliance': compliance
    }
    return response


@timer
def deployment_frequency(repositories:list[dict[str,str]],
                        start:date, end:date,
                        parent_team:str, g:Github) -> dict[str, dict[str, dict[str,Any]]]:
    """Fetch aggregated deployment information for all repositories passed"""
    logging.debug('deployment frequency data', repository_config=repositories)

    start_time:datetime = datetime.now(timezone.utc)
    # all the freq info
    all:dict[str, dict[str, Any]] = {}
    # stat items
    repository_names:list[str] = []
    weekdays:dict[str, int] = {}
    by_repository: dict[str, dict] = {}
    by_team: dict[str, dict] = {}
    l:int = len(repositories)
    for i, conf in enumerate(repositories):
        logging.debug('getting deployment_frequency for repo', repository_name=conf.get('repo'))
        repo = GithubRepository(g, conf.get('repo'))
        repository_names.append(repo.name)
        logging.debug('repository name', name=repo.name)

        df:dict[str, dict[str, Any]] = repo.deployment_frequency(start, end, conf.get('branch'), conf.get('workflow') )
        logging.info(f'[{i+1}/{l}] deployment_frequency for repo [{repo.name}]', repo=repo.name, df=df)
        # by repo name
        by_repository[repo.name] = df
        # by teams - merge together
        teams:list[Team] = repo.teams(parent_team)
        for month,values in df.items():
            for t in teams:
                name:str = t.slug
                if name not in by_team:
                    by_team[name] = {}
                if month not in by_team[name]:
                    by_team[name][month] = {}

                for k,v in values.items():
                    by_team[name][month][k] = by_team[name].get(month, {}).get(k, 0) + v

        # by month - merge together
        for key,values in df.items():
            weekdays[key] = weekdays_in_month( to_date(key) )
            # set default
            if key not in all:
                all[key] = {}
            # merge in values
            for k, v in values.items():
                all[key][k] = all[key].get(k, 0) + v

    end_time:datetime = datetime.now(timezone.utc)
    duration = human_duration(start_time, end_time)

    response:dict[str, dict[str, dict[str,Any]]] = {
        'meta': {
            'repositories': repository_names,
            'weekdays': weekdays,
            'months': year_month_list(start, end),
            'teams': list(by_team.keys()),
            'execution_time': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'duration': duration,
            }
        },
        'by_month': all,
        'by_repository': by_repository,
        'by_team': by_team,
    }
    logging.debug('deployment frequencies', result=response)

    return response
