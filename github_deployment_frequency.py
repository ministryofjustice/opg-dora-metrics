import os
import time
import json
import argparse
from argparse import RawTextHelpFormatter
from datetime import datetime, timezone, date
from dateutil.relativedelta import relativedelta
from pprint import pp
from github import Github
from github.Repository import Repository
from app.reports.writer import writer
from app.data.remote.github.repository import repositories_for_org_and_team, repositories_from_slugs
from app.data.remote.github.localise import localise_repo, localise_pull_requests, localise_workflow_runs, localise_teams
from app.dates.duration import duration
from app.reports.github_deployment_frequency.report import reports
from app.log.logger import logging, lvl
from app.decorator import TRACK_DURATIONS

TRACK_DURATIONS['enabled'] = True

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
    logging.info(f'[Deployment Frequency] starting', current_level=lvl)

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
    pattern:str = ' live'
    branch:str = 'main'

    # now convert them!
    localised:list[dict] = []
    # could be prs or workflows
    local_deployments:list = []
    local_teams:list = []

    vs:float = time.perf_counter()

    total:int = len(repositories)
    for i, repo in enumerate(repositories):
        s:float = time.perf_counter()

        logging.info(f'[{i+1}/{total}] [{repo.full_name}] converting to local store')
        # get local details
        local, _ = localise_repo(repository=repo)
        teams, _ = localise_teams(repository=repo, filter_by_parent_slug=args.team_parent)
        localised.append(local)
        # get the workflow / pr data
        deploys, _ = localise_workflow_runs(repository=repo,
                                                 start=start,
                                                 end=end,
                                                 branch=branch,
                                                 pattern=pattern)
        if len(deploys) <= 0:
            logging.warn(f'[{i+1}/{total}] [{repo.full_name}] using pull requests as a proxy')
            deploys, _ = localise_pull_requests(repository=repo,
                                                start=start, end=end, branch=branch)

        local_teams += teams
        local_deployments += deploys
        e:float = time.perf_counter()
        loop_dur = e - s
        logging.info(f'[{i+1}/{total}] [{repo.full_name}] duration: [{loop_dur}]', loop_duration=loop_dur, total_dur=(e-vs))
        # flag any slow calls
        if loop_dur > 60:
            logging.error(f'[{repo.full_name}] over 60 seconds!')
        elif loop_dur > 30:
            logging.warn(f'[{repo.full_name}] over 30 seconds!')

    # de-dup teams
    uteam:dict = {t['id']: t for t in local_teams}
    local_teams = uteam.values()

    end_time:datetime = datetime.now(timezone.utc)
    dur:str = duration(start=start_time, end=end_time)
    timings:dict = {'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'duration': dur}

    logging.info(f'[Deployment Frequency] generating report documents')

    report_data:dict = reports(repositories=localised,
                               args=args.__dict__,
                               start=start,
                               end=end,
                               timings=timings,
                               deployments=local_deployments,
                               teams=local_teams)

    output_dir:str = './outputs/github_deployment_frequency/'
    writer(report_data=report_data, output_dir=output_dir)

    logging.info(f'[Deployment Frequency] completed in [{dur}].')

    if TRACK_DURATIONS['enabled']:
        tracked = sorted(TRACK_DURATIONS['data'], key=lambda i: i['duration'], reverse=True)
        with open('times.json', 'w+') as f:
            json.dump(tracked, f, sort_keys=True, indent=2, default=str)


if __name__ == "__main__":
    main()
