import argparse
import os
import json
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta
from typing import Any
from pprint import pp
from github import Github
from github.Repository import Repository
from app.reports.writer import writer
from app.reports.service_uptime.report import reports
from app.data.github.remote.localise import localise_workflow_runs, localise_artifacts
from app.data.github.remote.repository import repositories_from_slugs
from app.dates.duration import duration

def main():
    start_time:datetime = datetime.now(timezone.utc)

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
    end_time:datetime = datetime.now(timezone.utc)
    dur:str = duration(start=start_time, end=end_time)
    timings:dict = {'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'duration': dur}



    report_data:dict = reports(artifacts=artifacts,
                               token=github_token,
                               start=start,
                               end=end,
                               args=args.__dict__,
                               timings=timings,
                               )
    output_dir:str = './outputs/service_uptime/'
    writer(report_data=report_data, output_dir=output_dir)

if __name__ == "__main__":
    main()
