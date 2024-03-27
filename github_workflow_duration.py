import argparse
import os
import logging
from gh.auth import init
from gh.workflows import workflow_total_durations
from github import Github
from github.Repository import Repository



def main() :
    logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper())
    # handle args
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", help="Full name of the repository, including owner", required=True, type=str)
    parser.add_argument("--workflow", help="Workflow id to calculate the duration of", required=True, type=int)
    args = parser.parse_args()
    # setup auth
    token = str( os.environ.get("GH_TOKEN", "" ))
    g:Github
    g, _, _ = init(token)
    # find the repo
    r:Repository = g.get_repo(str(args.repository))

    durations:dict = workflow_total_durations(r, int(args.workflow))
    # output all values

    for key, value in durations.items():
        print(f'{key}={value}')


if __name__ == "__main__":
    main()
