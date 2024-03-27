import logging
from github.Team import Team
from github.PaginatedList import PaginatedList
from github.Repository import Repository

def repositories_and_workflows(team:Team, workflow_pattern:str = " live") -> list[str]:
    logging.debug(f"Generating list of team repositories for [{team.name}]")
    repos:PaginatedList[Repository] = team.get_repos()
    found:list[str] = []

    for r in repos:
        found.append(f'{r.full_name}:{r.default_branch}:{workflow_pattern}')
    return found
