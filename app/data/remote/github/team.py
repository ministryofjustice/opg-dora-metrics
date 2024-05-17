from github import Github
from github.Repository import Repository
from github.Team import Team


def teams(repository:Repository) -> list[Team]:
    """Return the teams for this repository"""
    return [t for t in repository.get_teams()]

