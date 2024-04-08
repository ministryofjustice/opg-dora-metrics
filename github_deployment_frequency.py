import argparse
import os
from github import Github, Organization, Team
from github.Repository import Repository

from gh.auth import init
from metrics.github import deployment_frequency
from log.logger import logging
from argparse import RawTextHelpFormatter
from converter.convert import to
from utils.args import date_range_split, date_from_duration, github_organisation_and_team, github_repository_branch_workflow_list


from pprint import pp


def main() :

    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)

    ## cli args for report start / end dates
    dates = parser.add_argument_group("Reporting period (fixed or relative)")
    dates_mx = dates.add_mutually_exclusive_group(required=True)
    dates_mx.add_argument('--date-range',
                          help='Date range - format: 2024-01..2024-03',
                          type=date_range_split)
    dates_mx.add_argument('--duration',
                          help='Number of months ago to use as start date, with end date being today',
                          type=date_from_duration)

    ## args for which repositories
    repoconfig = parser.add_argument_group("Repositories to report on")
    repoconfig_mx = repoconfig.add_mutually_exclusive_group(required=True)
    repoconfig_mx.add_argument("--org-team",
                            help="Specify the organisation and team slugs (<org-slug>:<team-slug>)",
                            type=github_organisation_and_team)
    repoconfig_mx.add_argument("--repo-branch-workflow",
                            action='append',
                            help="Specify multiple repo-branch-workflow patterns (<repo-full-name>:<branch>:<workflow-name>)",
                            type=github_repository_branch_workflow_list)


    args = parser.parse_args()

    date_range = args.duration if args.duration is not None else args.date_range
    repoconfig = args.org_team if args.org_team is not None else args.repo_branch_workflow
    logging.info("running report", date_range=date_range, repoconfig=repoconfig)

    g:Github
    team:Team
    repository_report_config: list[dict[str,str]] = []
    # if this is dict, then we need to fetch all repos for this org
    if type(repoconfig) == dict:
        g, _, team = init(token=os.environ.get("GITHUB_ACCESS_TOKEN", None ),
                            organisation_slug=repoconfig['org'],
                            team_slug=repoconfig['team'])
        # get repos for team and covnert to same format used for listed versions
        logging.warn("generating repo config from team repositories", team=team.name() )
        repository_report_config = [{'repo':i.full_name, 'branch': i.default_branch, 'workflow':' live'}  for i in team.get_repos() ]
    else:
        g, _, _ = init(token=os.environ.get("GITHUB_ACCESS_TOKEN", None ) )
        repository_report_config = list(args.repo_branch_workflow)


    data = deployment_frequency(repositories=repository_report_config,
                                start=date_range['start'],
                                end=date_range['end'],
                                g=g
                                )
    data['args'] = args.__dict__
    pp(data)

if __name__ == "__main__":
    main()
