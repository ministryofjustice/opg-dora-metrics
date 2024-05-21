import argparse
import os
import json
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta
from typing import Any
from pprint import pp
from github import Github
from github.Repository import Repository
from app.reports.service_uptime.report import reports
from app.data.github.remote.localise import localise_repo, localise_workflow_runs, localise_artifacts
from app.data.github.remote.repository import repositories_from_slugs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-repository',
                        help='Name of repository that runs the daily reports that we want to fetch and merge.',
                        default='ministryofjustice/opg-technical-guidance')
    parser.add_argument('--duration',
                          help='Number of months ago to use as start date, with end date being today',
                          default=1)
    parser.add_argument('--startdate',
                          help='Month we started to track uptime reports',
                          default='2024-05'
                          )
    args = parser.parse_args()

    end:date = datetime.now(timezone.utc).date()
    start:date = end - relativedelta(months=int(args.duration))

    github_token = os.environ.get("GITHUB_ACCESS_TOKEN", None )
    g:Github = Github(github_token)
    slug:str = args.source_repository
    branch:str = "main"

    repos:list[Repository] = repositories_from_slugs(g=g,
                                                     repository_slugs=[slug],
                                                     exclude_archived=False)
    #
    source_repository:Repository = repos[0]
    pattern:str = 'daily service uptime'
    # get all the workflow runs that match the daily uptime pattern name
    _, workflow_runs = localise_workflow_runs(repository=source_repository,
                                              start=start,
                                              end=end,
                                              branch=branch,
                                              pattern=pattern,
                                              localise=False)

    # get the artifacts for each workflow run
    artifacts, _ = localise_artifacts(workflow_runs=workflow_runs)
    ##
    report_data:dict = reports(artifacts=artifacts, token=github_token)


if __name__ == "__main__":
    main()
