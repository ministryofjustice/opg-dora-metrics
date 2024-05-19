import os
import json
from datetime import date, datetime, timezone
from typing import Any
from pprint import pp
from jinja2 import Environment, FileSystemLoader, Template

__output_directory__:str = './outputs/github_repository_standards/'
__template_directory__:str = './app/reports/github_repository_standards/templates/'


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

    has_passed_baseline:str = "✅" if repository['standards']['status']['baseline'] else "❌"
    has_passed_extended:str = "✅" if repository['standards']['status']['extended'] else "❌"
    output:str = template.render(now=t,
                                 has_passed_baseline=has_passed_baseline,
                                 has_passed_extended=has_passed_extended,
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

def generate_reports(repositories:list[dict], duration:str) -> None:
    """Create the report files for each report"""

    detailed:dict[str] = detailed_reports(repositories=repositories)
    overview:str = overview_report(repositories=repositories, duration=duration)

    dir:str = __output_directory__
    # write all the detailed reports
    for key, report in detailed.items():
        path:str = f'{dir}{key}'
        os.makedirs(path, exist_ok=True)
        with open(f'{path}/index.html.md.erb', 'w+') as f:
            f.write(report)

    # now the overview
    path:str = f'{dir}/index.html.md.erb'
    with open(path, 'w+') as f:
        f.write(overview)


def report(response:dict) -> None:
    """"""

    repositories:list = response['result']
    duration:str = response['meta']['timing']['duration']

    dir:str = __output_directory__
    os.makedirs(dir, exist_ok=True)
    path:str = f'{dir}/raw.json'
    with open(path, 'w+') as f:
        json.dump(response, f, sort_keys=True, indent=2, default=str)

    generate_reports(repositories=repositories, duration=duration)
