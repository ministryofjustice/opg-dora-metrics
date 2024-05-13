import os
import json
from datetime import date, datetime,timezone
import calendar
from typing import Any
from pprint import pp
from jinja2 import Environment, FileSystemLoader, Template

_path:str = './outputs/service_uptime/'
_templates:str = './templates/service_uptime/'


def _by_month(by_month:dict[str, dict[str,float]], months:list[str], duration:str=None):
    """Create a top level monthly_uptime page and then a page for each month"""
    loader:FileSystemLoader = FileSystemLoader(_templates)
    env:Environment = Environment(loader=loader)
    t:str = datetime.utcnow().strftime('%Y-%m-%d')

    # latest month of things
    template:Template = env.get_template('by_month.md.jinja')
    output:str = template.render(now=t, by_month=by_month, duration=duration, months=months)
    os.makedirs(_path, exist_ok=True)
    with open(f'{_path}latest.html.md.erb', 'w+') as f:
        f.write(output)
    # now we generate one per month
    for year_month in months:
        ym:date = datetime.strptime(year_month, '%Y-%m').date()
        # reduce the months to just this month
        output:str = template.render(now=t,
                                     by_month=by_month,
                                     duration=duration,
                                     months=[year_month],
                                     report_time=f" for {year_month}",
                                     review_in=120,
                                     )
        path:str = f'{_path}by_month/{ym.strftime('%Y-%m')}/'
        os.makedirs(path, exist_ok=True)
        with open(f'{path}index.html.md.erb', 'w+') as f:
            f.write(output)

def _by_day(by_day:dict[str, dict[str,float]], months:list[str], all_days:list[str], duration:str=None):
    """Create a daily breakdown for each month"""
    loader:FileSystemLoader = FileSystemLoader(_templates)
    env:Environment = Environment(loader=loader)
    now = datetime.now(timezone.utc)
    t:str = now.strftime('%Y-%m-%d')

    template:Template = env.get_template('by_day.md.jinja')

    # now we generate one per month
    for year_month in months:
        ym:date = datetime.strptime(year_month, '%Y-%m').date()
        month_str:str = ym.strftime('%Y-%m')
        max:int = calendar._monthlen(ym.year, ym.month)
        if ym.year == now.year and ym.month == now.month:
            max = now.day

        days:list = [ym.replace(day=i).strftime('%Y-%m-%d') for i in range(1, max+1)]
        # reduce the months to just this month
        output:str = template.render(now=t,
                                     month=month_str,
                                     by_day=by_day,
                                     duration=duration,
                                     days=days,
                                     report_time=f" for {year_month}",
                                     review_in=120,
                                     )
        path:str = f'{_path}by_day/{ym.strftime('%Y-%m')}/'
        os.makedirs(path, exist_ok=True)
        with open(f'{path}index.html.md.erb', 'w+') as f:
            f.write(output)



def report(data:dict[str, dict[str, dict[str,Any]]]):
    """Generate all the report files for service uptime"""
    # create by_month report
    months:list = data.get('meta').get('months')
    days:list = data.get('meta').get('days')
    duration:str = data.get('meta').get('execution_time').get('duration')
    by_month = data.get('by_month')
    by_day = data.get('by_day')

    _by_month(by_month, months, duration)
    _by_day(by_day, months, days, duration)

    # track the raw data file
    ts_iso:str = data.get('meta').get('execution_time').get('start')
    ts:datetime = datetime.fromisoformat(ts_iso)

    dir:str = f'{_path}source-data/'
    os.makedirs(dir, exist_ok=True)
    rawfile:str = f'{dir}{ts.strftime('%Y-%m-%d')}.json'
    with open(rawfile, 'w+') as f:
        json.dump(data, f, sort_keys=True, indent=2, default=str)
