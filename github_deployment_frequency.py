import argparse
import os
import json
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

def write(outputfile:str, all_results:dict):
    if outputfile is not None:
        with open(outputfile, 'w+') as fp:
            json.dump(all_results, fp)

def stats(justresults:dict) -> dict:
    """Generate monhtly stats for the all"""
    totals:dict = {}
    for _, res in justresults.items():
        for ym, stats in res.items():
            current_success = totals.get(ym, {'successes':0}).get('successes')
            current_total = totals.get(ym, {'total':0}).get('total')
            s = current_success + stats['success']

            for k,v in stats.items():
                if k != "weekdays" and k != "average_success_per_day" and k != "merge_based":
                    current_total += v

            totals[ym] = {
                'days': stats['weekdays'],
                'successes': s,
                'average_success': round(s / stats['weekdays'], 2),
                'total': current_total,
                'average': round(current_total / stats['weekdays'], 2)
            }
    return totals

def main() :
    logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper())
    # handle args
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument("--start", help="Start date (format: 2024-02)", required=False, type=str)
    parser.add_argument("--end", help="End date (format: 2024-04)", required=False, type=str)
    parser.add_argument("--o", help="filename to write results into", required=False, default="./github_deployment_frequency.json")

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
    outputfile = args.o
    # setup auth
    token = str( os.environ.get("GITHUB_ACCESS_TOKEN", "" ))
    g:Github

    repo_and_workflows:list = []
    # if this has been triggered with org / team setup, then
    # generate a list that matches input from the github api
    #  Note: the workflow is assumed to contain ' live', as in 'path to live'
    if args.rwl is None:
        org_slug, team_slug = map(str, args.ot.split(':'))
        g, _, team = init(token, org_slug, team_slug)
        repo_and_workflows = repositories_and_workflows(team)
    else:
        g, _, _ = init(token)
        repo_and_workflows = list(args.rwl)

    start:date = datetime.strptime(str(args.start), '%Y-%m').date()
    end:date = datetime.strptime(str(args.end), '%Y-%m').date()

    all_results:dict = {
        'params': {
            'start': f'{start}',
            'end': f'{end}',
            'org-team': args.ot,
            'repo-branch-workflow': args.rwl
        },
        'stats': {},
        'results': {}
    }
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

        all_results['results'][r.full_name] = res
        # write results to file as we go along for debugging
        write(outputfile, all_results)


    # now work out averages overall
    justresults = all_results['results']
    all_results['stats'] = stats(justresults)

    write(outputfile, all_results)

if __name__ == "__main__":
    main()
