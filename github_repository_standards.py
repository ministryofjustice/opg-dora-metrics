from typing import Any
from pprint import pp
import os
import argparse
from argparse import RawTextHelpFormatter
from datetime import datetime, timezone
from pathlib import Path

from github import Github
from github.Repository import Repository
from app.data.remote.github.repository import repositories_for_org_and_team, repositories_from_slugs
from app.data.remote.github.localise import localise_repo
from app.dates.duration import duration
from app.log.logger import logging
from app.reports.github_repository_standards.report import reports
from app.reports.writer import writer

def main() :

    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('--exclude-archived',
                        help='Decide if we include archived repositories or not in the report',
                        default=True,
                        action=argparse.BooleanOptionalAction)
    ## args for which repositories
    repoconfig = parser.add_argument_group("Repositories to report on")
    repoconfig_mx = repoconfig.add_mutually_exclusive_group(required=True)
    repoconfig_mx.add_argument("--org-team",
                               help="Specify the organisation and team slugs (<org-slug>:<team-slug>)")
    repoconfig_mx.add_argument("--repository",
                               action='append',
                               help="Specify multiple repositories (<repo-full-name>)")

    args = parser.parse_args()
    logging.info(f'[Standards Compliance] starting')

    github_token = os.environ.get("GITHUB_ACCESS_TOKEN", None )
    g:Github = Github(github_token)

    #### fetch the repositories
    start_time:datetime = datetime.now(timezone.utc)
    repositories:list[Repository] = []
    if args.org_team is not None:
        org, team = map(str, args.org_team.split(':'))
        repositories = repositories_for_org_and_team(g=g,
                                                     organisation_slug=org,
                                                     team_slug=team,
                                                     exclude_archived=bool(args.exclude_archived))
    else:
        repositories = repositories_from_slugs(g=g,
                                               repository_slugs=list(args.repository),
                                               exclude_archived=bool(args.exclude_archived))

    # now convert them!
    localised:list[dict] = []
    total:int = len(repositories)
    for i, repo in enumerate(repositories):
        s:datetime = datetime.now(timezone.utc)
        logging.info(f'[{i+1}/{total}] [{repo.full_name}] converting to local store')
        local_repo, _  = localise_repo(repository=repo)
        localised.append(local_repo)

        e:datetime = datetime.now(timezone.utc)
        d = duration(start=s, end=e)
        logging.info(f'[{i+1}/{total}] [{repo.full_name}] duration: [{d}]', loop_duration=d)

    end_time:datetime = datetime.now(timezone.utc)
    logging.info(f'[Standards Compliance] generating report documents')

    dur:str = duration(start=start_time, end=end_time)
    timings:dict = {'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'duration': dur}

    report_data:dict = reports(repositories=localised, args=args.__dict__, timings=timings)
    output_dir:str = './outputs/github_repository_standards/'

    writer(report_data=report_data, output_dir=output_dir)
    logging.info(f'[Standards Compliance] completd in [{dur}].')


if __name__ == "__main__":
    main()
