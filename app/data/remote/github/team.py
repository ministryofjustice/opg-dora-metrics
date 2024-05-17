from github import Github
from github.Repository import Repository
from github.Team import Team

from app.log.logger import logging

def teams(repository:Repository) -> list[Team]:
    """Return the teams for this repository"""
    logging.debug('getting teams', repo=repository.full_name)
    teams:list[Team] = [t for t in repository.get_teams()]
    logging.info(f'[{repository.full_name}] (teams) found [{len(teams)}] ', repo=repository.full_name)
    
    return teams

