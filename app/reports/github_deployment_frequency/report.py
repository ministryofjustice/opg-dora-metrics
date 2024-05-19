import os
import json
from datetime import date, datetime, timezone
from typing import Any
from pprint import pp
from jinja2 import Environment, FileSystemLoader, Template
from app.utils.dates.ranges import date_range, Increment
from app.utils.dates.duration import weekdays_in_month

__output_directory__:str = './outputs/github_deployment_frequency/'
__template_directory__:str = './app/reports/github_deployment_frequency/templates/'

# def __teams__(repositories:dict) -> list:
#     """Get all the teams"""
#     teams:list[dict] = []
#     for r in repositories:
#         for t in r['teams']:
#             teams.append(t)
#     return teams


# def __merger__(repositories:dict) -> list:
#     """Merge all workflow runs and pull requests for all repos into one source"""
#     data:list = []
#     for r in repositories:
#         if len(r['workflow_runs']) > 0:
#             for wr in r['workflow_runs']:
#                 wr['repository'] = r['full_name']
#                 wr['teams'] = r['teams']
#                 data.append(wr)
#         elif len(r['pull_requests']) > 0:
#             for pr in r['pull_requests']:
#                 pr['repository'] = r['full_name']
#                 pr['teams'] = r['teams']
#                 data.append(pr)
#     return data


# def __counts_by_date__(data:list[dict], fmt:str='%Y-%m') -> dict:
#     """Return a dict grouping the data by a date field in the format passed"""
#     counts:dict = {}
#     for item in data:
#         is_workflow:bool = 'created_at' in item.keys()
#         date_str:str = item['created_at'] if is_workflow else item['merged_at']
#         date_value:datetime = datetime.fromisoformat(date_str)
#         key:str = date_value.strftime(fmt)
#         if key not in counts:
#             counts[key] = 0
#         counts[key] += 1
#     return counts

# def __weekdays__(dates:list[date], fmt:str='%Y-%m') -> dict:
#     """"""
#     weekdays:dict[str, int] = {d.strftime(fmt):weekdays_in_month(d)  for d in dates}
#     return weekdays


# def by_month(data:list[dict],
#             dates:list[date],
#             fmt:str = '%Y-%m',
#             ) -> dict:
#     """"""
#     # generate the skel of the totals
#     totals: dict = {d.strftime(fmt):0 for d in dates}
#     # get the counts by month
#     counters: dict = __counts_by_date__(data=data, fmt=fmt)
#     # merge those together
#     for k, v in counters.items():
#         totals[k] = v
#     # work out week days
#     weekdays:dict = __weekdays__(dates=dates, fmt=fmt)
#     # now merge all of these together
#     by_month:dict[str, dict[str, int|float]] = {}
#     for ym, count in totals.items():
#         by_month[ym] = {
#             'total': count,
#             'weekdays': weekdays[ym],
#             'average_per_day': (count / weekdays[ym])
#         }

#     return by_month

# def by_month_report(data:list[dict],
#             duration:str,
#             dates:list[date],
#             fmt:str = '%Y-%m',
#             ) -> None:

#     per_month_data = by_month(data=data, dates=dates, fmt=fmt)
#     loader:FileSystemLoader = FileSystemLoader(__template_directory__)
#     env:Environment = Environment(loader=loader)
#     template:Template = env.get_template('by_month.md.jinja')
#     t:str = datetime.now(timezone.utc).strftime('%Y-%m-%d')

#     # generate report for all
#     output:str = template.render(now=t,
#                                  duration=duration,
#                                  by_month=per_month_data,
#                                  )

#     path:str = f'{__output_directory__}by_month'
#     os.makedirs(path, exist_ok=True)
#     with open(f'{path}/index.html.md.erb', 'w+') as f:
#         f.write(output)

#     # now do one for each month
#     for ym, month in per_month_data.items():
#         path:str = f'{__output_directory__}by_month/{ym}'
#         os.makedirs(path, exist_ok=True)
#         per:str = template.render(now=t, duration=duration, by_month={ym: month} )
#         with open(f'{path}/index.html.md.erb', 'w+') as f:
#             f.write(per)



# def report(response:dict) -> None:
#     """"""
#     repositories:list = response['result']
#     duration:str = response['meta']['timing']['duration']
#     start:date = date.fromisoformat(response['meta']['report']['start'])
#     end:date = date.fromisoformat(response['meta']['report']['end'])
#     dates:list[date] = date_range(start=start, end=end, inc=Increment.MONTH)
#     team_filter:str = response['meta']['args']['team_parent']

#     dir:str = __output_directory__
#     os.makedirs(dir, exist_ok=True)
#     path:str = f'{dir}/raw.json'
#     with open(path, 'w+') as f:
#         json.dump(response, f, sort_keys=True, indent=2, default=str)


#     merged_workflow_runs_and_prs = __merger__(repositories=repositories)

#     pp(team_filter)
#     teams:list = __teams__(repositories=repositories)
#     pp(teams)

#     # by_month_report(data=merged_workflow_runs_and_prs, duration=duration, dates=dates)
