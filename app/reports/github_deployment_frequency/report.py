import os
import json
from datetime import date, datetime, timezone
from typing import Any
from pprint import pp
from jinja2 import Environment, FileSystemLoader, Template
from app.dates.ranges import date_range_as_strings, Increment
from app.dates.duration import weekdays_in_month
from app.data.github.remote.localise import localise_pull_requests, localise_workflow_runs

__template_directory__:str = './app/reports/github_deployment_frequency/templates/'

def deployments_per_month(deployments:list, months:list[str]) -> dict[str, tuple[int,float]]:
    """"""
    per_month:dict = {ym:(0,0.0) for ym in months}
    for deploy in deployments:
        month:date = datetime.fromisoformat(deploy['date'])
        weekdays:int = weekdays_in_month(month)
        ym:str = month.strftime('%Y-%m')
        if ym not in per_month:
            per_month[ym] = (0, 0.0)
        count, a = per_month[ym]
        count += 1
        avg:float = count / weekdays
        per_month[ym] = (count, avg)

    return per_month

def deployments_per_repo_per_month(deployments:list,
                                         repositories:list,
                                         months:list[str]) -> dict[str, dict[str]]:
    """"""
    per_repo_per_month:dict = {}
    for r in repositories:
        deploys:list = [d for d in deployments if d['repository_id'] == r['id']]
        per_repo_per_month[r['full_name']] = deployments_per_month(deployments=deploys, months=months)
    return per_repo_per_month

def deployments_per_team_per_month(deployments:list,
                                   teams:list,
                                   months:list[str]) -> dict[str, dict[str]]:
    """"""
    per_team_per_month:dict = {}
    for t in teams:
        slug:str = t['slug']
        deploys:list = []
        # find deployments that are for the repo this team uses
        for dep in deployments:
            if slug in dep['teams']:
                deploys.append(dep)
        per_team_per_month[slug] = deployments_per_month(deployments=deploys, months=months)
    return per_team_per_month


def report_by_team_by_month(by_team:dict[str], duration:str,
                            months:list[str],report_period:str=None) -> str:
    """"""
    loader:FileSystemLoader = FileSystemLoader(__template_directory__)
    env:Environment = Environment(loader=loader)
    template:Template = env.get_template('by_team.md.jinja')

    t:str = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    output:str = template.render(now=t,
                                 duration=duration,
                                 by_team=by_team,
                                 months=months,
                                 report_time=report_period,
                                 )
    return output

def report_by_repo_by_month(by_month:dict[str], by_repo:dict[str],
                            duration:str, months:list[str], report_period:str=None) -> str:
    """"""
    loader:FileSystemLoader = FileSystemLoader(__template_directory__)
    env:Environment = Environment(loader=loader)
    template:Template = env.get_template('by_repository.md.jinja')

    t:str = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    output:str = template.render(now=t,
                                 duration=duration,
                                 by_repo=by_repo,
                                 months=months,
                                 totals=by_month,
                                 report_time=report_period,
                                 )
    return output

def report_by_month(by_month:dict[str], duration:str,
                    months:list[str]) -> str:
    """"""
    loader:FileSystemLoader = FileSystemLoader(__template_directory__)
    env:Environment = Environment(loader=loader)
    template:Template = env.get_template('by_month.md.jinja')

    t:str = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    output:str = template.render(now=t,
                                 duration=duration,
                                 by_month=by_month,
                                 )
    return output


def reports(repositories:list[dict],
            teams:list[dict],
            deployments:list[dict],
            start:date,
            end:date,
            args:dict,
            timings:dict) -> dict[str,str]:
    """"""

    duration:str = timings['duration']
    months:list = date_range_as_strings(start=start, end=end, inc=Increment.MONTH)
    per_month:dict = deployments_per_month(deployments=deployments, months=months)
    per_repo_per_month:dict = deployments_per_repo_per_month(deployments=deployments,
                                                                   repositories=repositories,
                                                                   months=months)
    per_team_per_month:dict = deployments_per_team_per_month(deployments=deployments,
                                                             teams=teams,
                                                             months=months)
    # pp(per_team_per_month)

    report_data:dict = {
        # raw data for json output
        'raw.json': {
            'meta': {
                'args': args,
                'timings': timings,
            },
            'months': months,
            'repositories': repositories,
            'teams': teams,
            'deployments': {
                'all': deployments,
                'per_month': per_month,
                'per_repo_per_month': per_repo_per_month,
                'per_team_per_month': per_team_per_month,
            },
        },
    }

    # do the monthly reports
    report_data['by_month/index.html.md.erb'] = report_by_month(by_month=per_month,
                                                                months=months,
                                                                duration=duration)
    for ym in months:
        report_data[f'by_month/{ym}/index.html.md.erb'] = report_by_month(by_month={ym:per_month[ym]},
                                                                months=[ym],
                                                                duration=duration)
    # do teams
    report_data['by_team/index.html.md.erb'] = report_by_team_by_month(by_team=per_team_per_month,
                                                                months=months,
                                                                duration=duration)
    for ym in months:
        report_data[f'by_team/{ym}/index.html.md.erb'] = report_by_team_by_month(by_team=per_team_per_month,
                                                                months=[ym],
                                                                duration=duration, report_period=f'({ym})')
    # repos
    report_data['by_repository/index.html.md.erb'] = report_by_repo_by_month(by_repo=per_repo_per_month,
                                                                             by_month=per_month,
                                                                             months=months,
                                                                             duration=duration)
    for ym in months:
        report_data[f'by_repository/{ym}/index.html.md.erb'] = report_by_repo_by_month(by_repo=per_repo_per_month,
                                                                             by_month=per_month,
                                                                             months=[ym],
                                                                             duration=duration, report_period=f'({ym})')

    return report_data
