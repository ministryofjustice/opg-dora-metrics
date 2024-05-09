import argparse
import os
import json
from datetime import date
from typing import Any
from dateutil.relativedelta import relativedelta
from github.WorkflowRun import WorkflowRun

from models.github_repository import GithubRepository
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
    g, _, _ = init(token=token)

    slug:str = args.source_repository
    dates:dict[str, date] = args.duration
    branch:str = "main"

    repo:GithubRepository = GithubRepository(g, slug)
    uptime = repo.uptime(token, dates['start'], dates['end'] + relativedelta(days=1), branch)



if __name__ == "__main__":
    main()
