import os
from typing import Any
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta

from app.data.github.local.artifact import download
from app.dates.ranges import Increment, date_range_as_strings
from app.dates.convert import to_date
from pprint import pp
from jinja2 import Environment, FileSystemLoader, Template

__template_directory__:str = './app/reports/service_uptime/templates/'
#####################
# group / counter helpers
#####################
def __per_month__(data:list[dict], months:list[str]) -> dict[str, tuple[float, int]]:
    """Group the uptim data by month with a tuple of total and counter for working out average later"""
    field:str = 'Timestamp'
    per_month:dict = {ym:(0.0, 0) for ym in months}
    for item in data:
        month:date = datetime.fromisoformat(item[field])
        ym:str = month.strftime('%Y-%m')
        if ym not in per_month:
            per_month[ym] = (0.0, 0)
        uptime, count = per_month[ym]
        count = count + 1
        uptime = (uptime + item['Average'])
        per_month[ym] = (uptime, count)

    return per_month

def __per_day__(data:list[dict], days:list[str]) -> dict[str, tuple[float, int]]:
    """Group by day"""
    field:str = 'Timestamp'
    per:dict = {i:(0.0, 0) for i in days}
    for item in data:
        month:date = datetime.fromisoformat(item[field])
        idx:str = month.strftime('%Y-%m-%d')
        if idx not in per:
            per[idx] = (0.0, 0)
        uptime, count = per[idx]
        count = count + 1
        uptime = (uptime + item['Average'])
        per[idx] = (uptime, count)

    return per


def __services__(data:list[dict]) -> list[str]:
    """Return just the service names"""
    services:dict[str,bool] = {}
    for item in data:
        service:str = item.get('Service')
        services[service] = True
    all:list = [s for s in services.keys()]
    all.sort()
    return all


def __group_by_service__(services:list[str], data:list[dict]) -> dict[str, list[dict]]:
    """Group the data into a dict with the service name being the key"""
    by_service:dict[str, list[dict]] = {}
    for service in services:
        by_service[service] = []
        for item in data:
            if item.get('Service') == service:
                by_service[service].append(item)

    return by_service


#####################
# generate structures
#####################
def per_service_per_month(services:list[str], data:list[dict], months:list[str]) -> dict[str, dict]:
    """Group data into services and months"""
    by_service:dict = __group_by_service__(services=services, data=data)
    by_service_by_month:dict = {s:{} for s in services}

    for service, items in by_service.items():
        by_month = __per_month__(data=items, months=months)
        by_service_by_month[service] = by_month

    return by_service_by_month

def per_service_per_day(services:list[str], data:list[dict], days:list[str]) -> dict[str, dict]:
    """Group data into services and months"""
    by_service:dict = __group_by_service__(services=services, data=data)
    by_service_by_day:dict = {s:{} for s in services}

    for service, items in by_service.items():
        by_day = __per_day__(data=items, days=days)
        by_service_by_day[service] = by_day

    return by_service_by_day

#####################
# reports
#####################

def report_by_month(by_service_by_month:dict[str],
                    months=list[str],
                    duration:str=None,
                    firstdate:date=None) -> str:
    """Generate a report for the month"""
    loader:FileSystemLoader = FileSystemLoader(__template_directory__)
    env:Environment = Environment(loader=loader)
    template:Template = env.get_template('by_month.md.jinja')

    now:datetime = datetime.now(timezone.utc)
    t:str = now.strftime('%Y-%m-%d')
    previous:list = []
    if firstdate is not None:
        previous:list = date_range_as_strings(firstdate, now.date())

    output:str = template.render(now=t,
                                 duration=duration,
                                 by_month=by_service_by_month,
                                 months=months,
                                 previous=previous)
    return output

def report_by_day(by_service_by_day:dict[str],
                 days=list[str],
                 month:str='',
                 duration:str=None) -> str:
    """Generate a report for the month"""
    loader:FileSystemLoader = FileSystemLoader(__template_directory__)
    env:Environment = Environment(loader=loader)
    template:Template = env.get_template('by_day.md.jinja')

    now:datetime = datetime.now(timezone.utc)
    t:str = now.strftime('%Y-%m-%d')

    output:str = template.render(now=t,
                                 duration=duration,
                                 report_time=f'for {month}',
                                 by_day=by_service_by_day,
                                 days=days)
    return output



def reports(artifacts:list[dict],
            token:str,
            start:date,
            end:date,
            args:dict,
            timings:dict,
            ) -> dict[str,Any]:
    """"""
    months:list = date_range_as_strings(start=start, end=end, inc=Increment.MONTH)
    all_days:list = date_range_as_strings(start=start, end=end, inc=Increment.DAY)
    now:datetime = datetime.now(timezone.utc).date()
    duration:str = timings['duration']
    firstdate:date = to_date(args['startdate'])
    # download all thee reports to get the raw data
    uptimes:list[dict] = []
    for artifact in artifacts:
        uptimes += download(artifact=artifact, token=token)

    # get the service names
    services:list[str] = __services__(data=uptimes)

    by_service_per_month:dict = per_service_per_month(services=services,
                                                 data=uptimes,
                                                 months=months)
    by_service_per_day:dict = per_service_per_day(services=services,
                                                  data=uptimes,
                                                  days=all_days)

    data:dict = {
        'raw.json': {
            'meta': {
                'args': args,
                'timings': timings,
            },
            'months': months,
            'artifacts': artifacts,
            'uptimes': {
                'all': uptimes,
                'per_service_per_month': by_service_per_month,
                'per_service_per_day': by_service_per_day,
            }
        },
    }

    # add a listing for the last month
    data['by_month/index.html.md.erb'] = report_by_month(by_service_by_month=by_service_per_month,
                                                         months=months,
                                                         duration=duration,
                                                         firstdate=firstdate)
    # now do each month so we have a historical record
    for ym in months:
        data[f'by_month/{ym}/index.html.md.erb'] = report_by_month(by_service_by_month=by_service_per_month,
                                                                months=[ym],
                                                                duration=duration)
        # generate the per day report for this month
        s:date = to_date(ym)
        e:date = to_date(ym) + relativedelta(months=1) - relativedelta(days=1)
        if e > now:
            e = now

        days:list = date_range_as_strings(start=s, end=e, inc=Increment.DAY)
        data[f'by_day/{ym}/index.html.md.erb'] = report_by_day(by_service_by_day=by_service_per_day,
                                                               days=days,
                                                               duration=duration,
                                                               month=ym)

    return data
