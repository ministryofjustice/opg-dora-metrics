import os
from datetime import date, datetime
from typing import Any
from pprint import pp

_path:str = './outputs/reports/deployment_frequency/'

def _by_month(by_month:dict[str, dict[str,Any]]):
    """"""
    pre:str =   f"""---
title: Releases per month
last_reviewed_on: {datetime.now().strftime('%Y-%m-%d')}
review_in: 3 months
---
# <%= current_page.data.title %>
Releases per month for all OPG owned repositories.
"""
    # create headers
    tbl:str = "| Month | Total | Average |\n| --- | --- | --- |\n"
    for month, v in by_month.items():
        tbl += f"| {month} | {v.get('total_success', 0 ) } | {v.get('average_success', 0.0):.2f} | \n"

    content:str = pre + tbl
    os.makedirs(_path, exist_ok=True)
    with open(f'{_path}by_month.md', 'w+') as f:
        f.write(content)

def _by_repository(by_repo:dict[str, dict[str,Any]], months:list[str]):
    """"""
    pre:str =   f"""---
title: Releases per repository, per month
last_reviewed_on: {datetime.now().strftime('%Y-%m-%d')}
review_in: 3 months
---
# <%= current_page.data.title %>
Releases per month for each repository.
"""
    rlen = 146
    ilen = 9
    tbl:str = f"| {'Repository': <{rlen}} | "
    split:str = f"|:{'':-<{rlen+1}}|"
    for m in months:
        tbl += f'{m:>{ilen}} | '
        split += f"{'':-<{ilen+1}}:|"
    tbl += '\n'
    split += '\n'
    tbl = tbl + split

    totals:dict[str, int] = {}
    for repo, values in by_repo.items():
        link:str = f'[{repo}](https://github.com/{repo})'
        tbl += f'| {link: <{rlen}} |'
        for m in months:
            v:dict = values.get(m, {})
            tbl += f'<span title="average per day: {v.get('average_success', 0.0):.2f}">{v.get('total_success', 0)}</span>  |'

            if m not in totals:
                totals[m] = 0
            totals[m] += v.get('total_success', 0)
        tbl += '\n'
    # add totals
    tbl += f"| {'TOTALS': <{rlen}} |"
    for m in months:
        tbl += f" {totals.get(m, 0):>{ilen}} |"
    tbl += '\n'

    os.makedirs(_path, exist_ok=True)
    with open(f'{_path}by_repository.md', 'w+') as f:
        f.write(tbl)


def _by_teams(by_team:dict[str, dict[str,Any]], months:list[str]):
    """"""
    pre:str =   f"""---
title: Releases per team, per month
last_reviewed_on: {datetime.now().strftime('%Y-%m-%d')}
review_in: 3 months
---
# <%= current_page.data.title %>
Releases per month for each team.
"""
    rlen = 50
    ilen = 9
    tbl:str = f"| {'Team': <{rlen}} | "
    split:str = f"|:{'':-<{rlen+1}}|"
    for m in months:
        tbl += f'{m:>{ilen}} | '
        split += f"{'':-<{ilen+1}}:|"
    tbl += '\n'
    split += '\n'
    tbl = tbl + split

    for team, values in by_team.items():
        tbl += f'| {team: <{rlen}} |'
        for m in months:
            v:dict = values.get(m, {})
            tbl += f'<span title="average per day: {v.get('average_success', 0.0):.2f}">{v.get('total_success', 0)}</span>  |'
        tbl += '\n'

    os.makedirs(_path, exist_ok=True)
    with open(f'{_path}by_team.md', 'w+') as f:
        f.write(tbl)



def report(data:dict[str, dict[str, dict[str,Any]]]):
    """Generate all the report files"""
    # create by_month report
    months:list = data.get('meta').get('months')
    teams: list = data.get('meta').get('teams')

    _by_month(data.get('by_month'))
    _by_repository(data.get('by_repository'), months)
    _by_teams(data.get('by_team'), months)
