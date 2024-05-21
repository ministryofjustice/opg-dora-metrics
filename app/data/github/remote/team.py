from github.Repository import Repository
from github.Team import Team
from app.decorator import timer
from app.logger import logging

@timer
def teams(repository:Repository, filter_by_parent_slug:str=None) -> list[Team]:
    """Return the teams for this repository"""
    logging.debug('getting teams', repo=repository.full_name)
    teams:list[Team] = []
    for t in repository.get_teams():
        parent_slug:str = t.parent.slug if t.parent is not None else '_'
        if filter_by_parent_slug is not None and parent_slug == filter_by_parent_slug:
            teams.append(t)
        elif filter_by_parent_slug is None:
            teams.append(t)

    logging.info(f'[{repository.full_name}] (teams) found [{len(teams)}] ', repo=repository.full_name)

    return teams
