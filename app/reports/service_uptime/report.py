from typing import Any
from datetime import date, datetime, timezone
from app.data.github.local.artifact import download
from pprint import pp

def __per_month__(data:list[dict], months:list[str]) -> dict[str, tuple[float, int]]:
    """"""
    field:str = 'Timestamp'
    per_month:dict = {ym:(0.0, 0) for ym in months}
    for item in data:
        month:date = datetime.fromisoformat(item[field])
        ym:str = month.strftime('%Y-%m')
        if ym not in per_month:
            per_month[ym] = (0.0, 0)
        uptime, count = per_month[ym]
        count = count + 1
        uptime = (uptime + item['Average']) / count
        per_month[ym] = (uptime, count)

    return per_month

def __services__(data:list[dict]) -> list[str]:
    """Return just the service names"""
    services:dict[str,bool] = {}
    for item in data:
        service:str = item.get('Service')
        services[service] = True
    return [s for s in services.keys()]



def per_month_per_service(data:list[dict], months:list[str]) -> dict:
    """"""
    by_service:dict[str, list[dict]] = {}
    for item in data:
        service:str = item.get('Service', None)



def reports(artifacts:list[dict], token:str) -> dict[str,Any]:
    """"""
    # download all thee reports to get the raw data
    uptimes:list[dict] = []
    for artifact in artifacts:
        uptimes += download(artifact=artifact, token=token)

    pp(artifacts)
    services:list[str] = __services__(data=uptimes)

    pp(services)
