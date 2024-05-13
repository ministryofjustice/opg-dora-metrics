import argparse
import os
import json
from argparse import RawTextHelpFormatter
from typing import Any

from gh.auth import init
from metrics.github import standards_compliance
from log.logger import logging
from utils.args import github_organisation_and_team
from reports.standards_compliance import report
from pprint import pp


def main() :

    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)

    ## args for which repositories
    repoconfig = parser.add_argument_group("Repositories to report on")

    repoconfig_mx = repoconfig.add_mutually_exclusive_group(required=True)
    repoconfig_mx.add_argument("--org-team",
                            help="Specify the organisation and team slugs (<org-slug>:<team-slug>)",
                            type=github_organisation_and_team)
    repoconfig_mx.add_argument("--repository",
                            action='append',
                            help="Specify multiple repositories (<repo-full-name>)")

    parser.add_argument('--exclude-archived',
                        help='Decide if we include archived repositories or not in the report',
                        default=True,
                        action=argparse.BooleanOptionalAction)


    args = parser.parse_args()

    repoconfig = args.org_team if args.org_team is not None else args.repository
    exclude_archived:bool = bool(args.exclude_archived)
    logging.info("running report", repoconfig=repoconfig, exclude_archived=exclude_archived)


    repos:list[str] = []
    if type(repoconfig) == dict:
        g, _, team = init(token=os.environ.get("GITHUB_ACCESS_TOKEN", None ),
                            organisation_slug=repoconfig['org'],
                            team_slug=repoconfig['team'])
        # get repos for team and covnert to same format used for listed versions
        logging.warn("generating repo config from team repositories", team=team.slug )
        repos = [i.full_name for i in team.get_repos() ]
    else:
        g, _, _ = init(token=os.environ.get("GITHUB_ACCESS_TOKEN", None ) )
        repos = list(args.repository)

    data:dict[str, dict[str, dict[str,Any]]] = standards_compliance(repos, g, exclude_archived)

    data['meta']['args'] = args.__dict__
    # dir to output to
    dir:str = './outputs/github_repository_standards/'
    os.makedirs(dir, exist_ok=True)
    # write raw json to file
    rawfile:str = f'{dir}./raw.json'
    with open(rawfile, 'w+') as f:
        json.dump(data, f, sort_keys=True, indent=2, default=str)

    report(data)

if __name__ == "__main__":
    main()
