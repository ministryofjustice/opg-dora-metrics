import argparse
import os
import logging
from argparse import RawTextHelpFormatter
from datetime import date, datetime
from gh.auth import init
from gh.team import repositories_and_workflows
from gh.merges import merges_to_branch
from gh.frequency import workflow_runs_by_month_fuzzy
from github import Github, Organization, Team
from github.Repository import Repository

from pprint import pp


def main() :
    logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper())
    # handle args
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument("--start", help="Start date (format: 2024-02)", required=False, type=str)
    parser.add_argument("--end", help="End date (format: 2024-04)", required=False, type=str)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--ot', '--organisation-and-team',
        help="Slug of org and team to generate list of repositories from.\n"
                "Format <organisation-slug>:<team-slug>\n"
                "Example: ministryofjustice:opg"
    )
    group.add_argument(
        "--rwl", "--repository-branch-and-workflow-list",
        action='append',
        help="Full repository name followed by branch then workflow name, seperated by a colon.\n"
            "Can specify multiple instances.\n"
            "Example (ministryofjustice/serve-opg:main: live$)",
    )

    args = parser.parse_args()

    # setup auth
    token = str( os.environ.get("GH_TOKEN", "" ))
    g:Github

    repo_and_workflows:list = []
    if args.rwl is None:
        org_slug, team_slug = map(str, args.ot.split(':'))
        g, _, team = init(token, org_slug, team_slug)
        repo_and_workflows = repositories_and_workflows(team)
    else:
        g, _, _ = init(token)
        repo_and_workflows = list(args.rwl)


    start:date = datetime.strptime(str(args.start), '%Y-%m').date()
    end:date = datetime.strptime(str(args.end), '%Y-%m').date()

    all_results:dict = {}
    i:int = 0
    t:int = len(repo_and_workflows)
    for rw in repo_and_workflows:
        i = i + 1
        repo, branch, workflow = map(str, rw.split(':'))
        logging.info(f"[{repo}] ({i}/{t}) [branch:{branch}] [workflow:{workflow}]")

        r:Repository = g.get_repo(repo)
        # Try to get workflow runs directly
        res = workflow_runs_by_month_fuzzy(workflow, r, start, end, branch)
        # If this fails, then get merges into the default branch
        if res is None:
            logging.warning(f"[{repo}] [branch:{branch}] [workflow:{workflow}] not found, using merge counter as proxy")
            res = merges_to_branch(r, start, end, branch)

        all_results[r.full_name] = res

    pp(all_results)


if __name__ == "__main__":
    main()
