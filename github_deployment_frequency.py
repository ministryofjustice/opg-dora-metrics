import os
import argparse
from argparse import RawTextHelpFormatter
from datetime import datetime, timezone, date
from dateutil.relativedelta import relativedelta
from pprint import pp
from github import Github
from github.Repository import Repository
from app.data.remote.github.repository import repositories_for_org_and_team, repositories_from_slugs
from app.data.remote.github.localise import to_local
from app.utils.dates.duration import duration
from app.reports.github_deployment_frequency.report import report
from app.log.logger import logging


def main() :

    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('--exclude-archived',
                        help='Decide if we include archived repositories or not in the report',
                        default=True,
                        action=argparse.BooleanOptionalAction)
    parser.add_argument('--duration',
                        help='Number of months ago to use as start date, with end date being today',
                        default=1)
    parser.add_argument('--team-parent',
                        help="Filter the team report to only include teams whose parent matches this slug (default: opg)",
                        default="opg"
                        )

    ## args for which repositories
    repoconfig = parser.add_argument_group("Repositories to report on")
    repoconfig_mx = repoconfig.add_mutually_exclusive_group(required=True)
    repoconfig_mx.add_argument("--org-team",
                               help="Specify the organisation and team slugs (<org-slug>:<team-slug>)")
    repoconfig_mx.add_argument("--repository",
                               action='append',
                               help="Specify multiple repositories (<repo-full-name>)")

    args = parser.parse_args()
    logging.info(f'[Deployment Frequency] starting')

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


    end:date = datetime.now(timezone.utc).date()
    start:date = end - relativedelta(months=int(args.duration))
    start = start.replace(day=1)
    pattern:str = ' live$'

    # now convert them!
    localised:list[dict] = []
    total:int = len(repositories)
    for i, repo in enumerate(repositories):
        logging.info(f'[{i+1}/{total}] [{repo.full_name}] converting to local store')
        # # get workflows and fallback to prs
        # local:dict = to_local(g=g,
        #                       repository=repo,
        #                       start=start,
        #                       end=end,
        #                       get_teams=True,
        #                       get_artifacts=False,
        #                       get_pull_requests=False,
        #                       get_workflow_runs=True,
        #                       workflow_run_pattern=pattern,
        #                       workflow_run_status='success',
        #                       pull_request_fallback=True)

        # localised.append(local)


    end_time:datetime = datetime.now(timezone.utc)
    dur:str = duration(start=start_time, end=end_time)
    logging.info(f'[Deployment Frequency] generating report documents')

    response:dict = {
        'meta': {
            'args': args.__dict__,
            'timing': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'duration': dur,
            },
            'report': {
                'pattern': pattern,
                'start': start.isoformat(),
                'end': end.isoformat(),
            },
        },
        'result': localised
    }
    #  report(response=response)
    # logging.info(f'[Deployment Frequency] completed in [{dur}].')


if __name__ == "__main__":
    main()
