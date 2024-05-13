from datetime import date, datetime, timezone
from typing import Any

from dateutil.relativedelta import relativedelta
from github import Github

from models.github_repository import GithubRepository
from utils.decorator import timer
from utils.dates import year_month_list, human_duration, date_list
from log.logger import logging

from pprint import pp


@timer
def service_uptime(repo_slug:str, start:date, end:date, branch:str, g:Github, token:str) -> dict[str, dict[str, dict[str,Any]]]:
    """"""
    end = end + relativedelta(days=1)
    logging.debug('service_uptime data', start=start, end=end)
    start_time:datetime = datetime.now(timezone.utc)

    repo:GithubRepository = GithubRepository(g, repo_slug)
    data:dict[str, dict[str, dict[str, float]]] = repo.uptime(token, start, end, branch)

    end_time:datetime = datetime.now(timezone.utc)
    duration = human_duration(start_time, end_time)

    response:dict[str, dict[str, dict[str,Any]]] = {
        'meta': {
            'months': year_month_list(start, end),
            'days': date_list(start, end, day=1, format='%Y-%m-%d'),
            'services': list(data['by_month'].keys()),
            'execution_time': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'duration': duration,
            }
        },
        'all_data_points': data['raw'],
        'by_month': data['by_month'],
        'by_day': data['by_day'],
    }

    return response
