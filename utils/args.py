import argparse
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta

from utils.dates import to_date
from pprint import pp
##############
# Argument handlers
##############

def date_from_duration(months_ago:str) -> dict[str, date]:
    """The argument passed assumes duration, so return start date `months_ago` and end date of today as a dict"""
    try:
        end:date = datetime.now(timezone.utc).date()
        start:date = end - relativedelta(months=int(months_ago))
        start = start.replace(day=1)
        return {'start': start, 'end':end, 'duration': months_ago}
    except Exception as e:
        raise argparse.ArgumentTypeError(f'argument must be postive int of months. error: {e}')


def date_range_split(date_range:str) -> dict[str, date]:
    """The argument (date_range) presumes format of YYYY-MM..YYYY-MM, splits the string by .. and converts to date objects in a dict"""
    try:
        s, e = map(str, date_range.split('..'))
        return {'start': to_date(s), 'end': to_date(e)}
    except Exception as e:
        raise argparse.ArgumentTypeError(f'argument must be <start-date>..<end-date>. error: {e}')

def github_organisation_and_team(org_team:str) -> dict[str, str]:
    """Presumes `org_team` is <org>:<team> formatted, splits and returns"""
    try:
        org, team = map(str, org_team.split(':'))
        return {'org':org, 'team':team}
    except Exception as e:
        raise argparse.ArgumentTypeError(f'argument must be <organisation>:<team>. error: {e}')

def github_repository_branch_workflow_list(args:str) -> dict[str, str]:
    """Handles one arg of <repo-name>:<branch>:<workflow-pattern> and returns it as a dict"""
    try:
        repo, branch, workflow = map(str, args.split(':'))
        return {'repo':repo, 'branch':branch, 'workflow':workflow}
    except Exception as e:
        raise argparse.ArgumentTypeError(f'argument must be in format <repo>:<branch>:<workflow>. error: {e}')
