import argparse

##############
# Argument handlers
##############

def github_organisation_and_team(args:str) -> dict[str, str]:
    """"""
    try:
        org, team = map(str, args.split(':'))
        return {'org':org, 'team':team}
    except:
        raise argparse.ArgumentTypeError('argument must be <organisation>:<team>')

def github_repository_branch_workflow_list(args:list[str]) -> list[dict[str, str]]:
    """"""
    parsed: list[tuple[str, ...]] = []
    for rwl in args:
        try:
            repo, branch, workflow = map(str, rwl.split(':'))
            parsed.append( {'repo':repo, 'branch':branch, 'workflow':workflow} )
        except:
            raise argparse.ArgumentTypeError('argument must be in format <repo>:<branch>:<workflow>')
    return parsed
