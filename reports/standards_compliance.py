import os
from datetime import date, datetime
from typing import Any
from pprint import pp
from jinja2 import Environment, FileSystemLoader, Template

_path:str = './outputs/github_repository_standards/'
_templates:str = './templates/github_repository_standards/'



def _list(data:dict[str, dict[str, dict[str,Any]]],  duration:str=None):
    """"""
    loader:FileSystemLoader = FileSystemLoader(_templates)
    env:Environment = Environment(loader=loader)
    template:Template = env.get_template('list.md.jinja')

    t:str = datetime.utcnow().strftime('%Y-%m-%d')
    output:str = template.render(now=t, data=data, duration=duration)
    os.makedirs(_path, exist_ok=True)
    with open(f'{_path}index.html.md.erb', 'w+') as f:
        f.write(output)


def report(data:dict[str, dict[str, dict[str,Any]]]):
    """Generate the report for repository standards"""
    # create by_month report
    duration:str = data.get('meta').get('execution_time').get('duration')
    _list(data, duration)
