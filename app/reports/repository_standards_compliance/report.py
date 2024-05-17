import os
from datetime import date, datetime, timezone
from typing import Any
from pprint import pp
from jinja2 import Environment, FileSystemLoader, Template

__output_directory__:str = './outputs/github_repository_standards/'
__template_directory__:str = './app/reports/repository_standards_compliance/templates//'


def single_report(repository:dict) -> str:
    """Generate a report string"""

    loader:FileSystemLoader = FileSystemLoader(__template_directory__)
    env:Environment = Environment(loader=loader)
    template:Template = env.get_template('repository.md.jinja')

    t:str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    name:str = repository['name']
    full_name:str = repository['full_name']
    link:str = f'https://github.com/ministryofjustice/{name}'

    public_private:str = 'private' if repository['private'] is True else 'public'
    report_link:str = f'https://operations-engineering-reports.cloud-platform.service.justice.gov.uk/{ public_private }-report/{ name }'
    baseline:dict = repository['standards']['baseline']
    extended:dict = repository['standards']['extended']
    information:dict = repository['standards']['information']
    output:str = template.render(now=t,
                                 link=link,
                                 name=name,
                                 full_name=full_name,
                                 public_private=public_private,
                                 baseline=baseline,
                                 extended=extended,
                                 report_link=report_link,
                                 information=information)
    return output

def detailed_reports(repositories:list[dict]) -> dict[str, str]:
    """Return a list of all individual reports for a series of repositories"""
    reports:dict = {r['name']: single_report(r) for r in repositories}
    return reports

def overview_report(repositories:list[dict], duration:str) -> str:
    """Generate a report listing current info for each repository"""

    loader:FileSystemLoader = FileSystemLoader(__template_directory__)
    env:Environment = Environment(loader=loader)
    template:Template = env.get_template('index.md.jinja')

    t:str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    total:int = len(repositories)

    baseline_passed:int = 0
    extended_passed:int = 0
    for r in repositories:
        baseline_passed += 1 if r['standards']['status']['baseline'] is True else 0
        extended_passed += 1 if r['standards']['status']['extended'] is True else 0
    output:str = template.render(now=t,
                                 total=total,
                                 baseline_passed=baseline_passed,
                                 extended_passed=extended_passed,
                                 repositories=repositories,
                                 duration=duration,
                                 )
    return output
