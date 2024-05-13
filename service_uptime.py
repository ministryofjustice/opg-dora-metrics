import argparse
import os
import json
from datetime import date
from typing import Any

from reports.service_uptime import report
from models.github_repository import GithubRepository
from metrics.uptime import service_uptime
from gh.auth import init
from log.logger import logging
from utils.args import date_from_duration
from pprint import pp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-repository',
                        help='Name of repository that runs the reports',
                        default='ministryofjustice/opg-technical-guidance')
    parser.add_argument('--duration',
                          help='Number of months ago to use as start date, with end date being today',
                          type=date_from_duration)
    args = parser.parse_args()

    token:str = os.environ.get("GITHUB_ACCESS_TOKEN", None )
    slug:str = args.source_repository
    dates:dict[str, date] = args.duration
    branch:str = "main"
    g, _, _ = init(token=token)

    data:dict[str, dict[str, dict[str,Any]]] = service_uptime(slug, dates['start'], dates['end'], branch, g, token)

    data['meta']['args'] = args.__dict__
    # dir to output to
    dir:str = './outputs/service_uptime/'
    os.makedirs(dir, exist_ok=True)
    # write raw json to file
    rawfile:str = f'{dir}./raw.json'
    with open(rawfile, 'w+') as f:
        json.dump(data, f, sort_keys=True, indent=2, default=str)

    report(data)



if __name__ == "__main__":
    main()
