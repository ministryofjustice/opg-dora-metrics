import os
from datetime import date, datetime
from typing import Any
from pprint import pp
from jinja2 import Environment, FileSystemLoader, Template

_path:str = './outputs/reports/deployment_frequency/'
_templates:str = './reports/templates/deployment_frequency/'

def _by_month(by_month:dict[str, dict[str,Any]]):
    """generate markdown report by month only"""

    loader:FileSystemLoader = FileSystemLoader(_templates)
    env:Environment = Environment(loader=loader)
    template:Template = env.get_template('by_month.erb')

    t:str = datetime.utcnow().strftime('%Y-%m-%d')
    output:str = template.render(now=t, by_month=by_month)
    os.makedirs(_path, exist_ok=True)
    with open(f'{_path}by_month.md', 'w+') as f:
        f.write(output)


def _by_repository(by_repo:dict[str, dict[str,Any]], months:list[str], totals:dict[str, dict[str,Any]] ):
    """generate markdown / html mix for repo per month"""
    loader:FileSystemLoader = FileSystemLoader(_templates)
    env:Environment = Environment(loader=loader)
    template:Template = env.get_template('by_repository.erb')

    t:str = datetime.utcnow().strftime('%Y-%m-%d')
    output:str = template.render(now=t, by_repo=by_repo, months=months, totals=totals)
    os.makedirs(_path, exist_ok=True)
    with open(f'{_path}by_repository.md', 'w+') as f:
        f.write(output)



def _by_teams(by_team:dict[str, dict[str,Any]], months:list[str]):
    """generate markdown / html mix for team per month"""

    loader:FileSystemLoader = FileSystemLoader(_templates)
    env:Environment = Environment(loader=loader)
    template:Template = env.get_template('by_team.erb')

    t:str = datetime.utcnow().strftime('%Y-%m-%d')
    output:str = template.render(now=t, by_team=by_team, months=months)
    os.makedirs(_path, exist_ok=True)
    with open(f'{_path}by_team.md', 'w+') as f:
        f.write(output)



def report(data:dict[str, dict[str, dict[str,Any]]]):
    """Generate all the report files for deployment frequency"""
    # create by_month report
    months:list = data.get('meta').get('months')
    teams: list = data.get('meta').get('teams')
    by_month = data.get('by_month')

    _by_month(by_month)
    _by_repository(data.get('by_repository'), months, by_month)
    _by_teams(data.get('by_team'), months)
