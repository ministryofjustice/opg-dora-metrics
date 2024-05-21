import os
import json
from datetime import date, datetime, timezone
from typing import Any
from pprint import pp
from jinja2 import Environment, FileSystemLoader, Template
from app.data.github.local.standards.repository_standards_compliance import repository_standards


__template_directory__:str = './app/reports/github_repository_standards/templates/'

def report_detailed(repository:dict, standards:dict[str,Any]) -> str:
    """Generate a report string"""

    repository['standards'] = standards
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

def report_index(repositories:list[dict], standards:dict[str, dict[str,Any]], duration:str) -> str:
    """Generate a report listing current info for each repository"""

    loader:FileSystemLoader = FileSystemLoader(__template_directory__)
    env:Environment = Environment(loader=loader)
    template:Template = env.get_template('index.md.jinja')

    t:str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    total:int = len(repositories)


    baseline_passed:int = 0
    extended_passed:int = 0
    for r in repositories:
        name:str = r['name']
        r['standards'] = standards[name]
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

def reports(repositories:list[dict], args:dict, timings:dict) -> dict[str,str]:
    """Generate a series of report data in mix of json and rendered templates to return"""

    duration:str = timings['duration']
    standards:dict = {r['name']:repository_standards(local_repository=r) for r in repositories}
    report_data:dict = {
        # raw data for json output
        'raw.json': {
            'meta': {
                'args': args,
                'timings': timings,
            },
            'repositories': repositories,
            'repository_standards': standards,
        },
        'index.html.md.erb': report_index(repositories=repositories, standards=standards, duration=duration),
    }

    for r in repositories:
        name:str = r['name']
        report_data[f'{name}/index.html.md.erb'] = report_detailed(r, standards[name])

    return report_data
