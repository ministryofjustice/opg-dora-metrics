from github import Github
from github.Repository import Repository
from github.Organization import Organization
from github.Team import Team
from app.logger import logging
from app.decorator import timer



@timer
def get_repository_by_slug(g:Github, slug:str) -> Repository:
    """Return a repository based on the slug"""
    logging.debug('getting repository', slug=slug)
    return g.get_repo(slug)

@timer
def repositories_for_org_and_team(g:Github,
                                  organisation_slug:str,
                                  team_slug:str,
                                  exclude_archived:bool=False) -> list[Repository]:
    """Use the organisation and team slugs passed to generate a list of repositories"""
    logging.debug('getting repositorys from org & team', org=organisation_slug, team=team_slug)
    org:Organization = g.get_organization(organisation_slug)
    team:Team = org.get_team_by_slug(team_slug)

    repos:list[Repository] = []
    for r in team.get_repos():
        if not exclude_archived or (exclude_archived and r.archived is False):
            repos.append(r)

    logging.info(f' (repository) found [{len(repos)}] repos', org=organisation_slug, team=team_slug)
    return repos

@timer
def repositories_from_slugs(g:Github,
                            repository_slugs:list[str],
                            exclude_archived:bool=False) -> list[Repository]:
    """Return a list of repositorys by finding them from the slugs passed"""
    logging.debug('getting repositories from slugs', slugs=repository_slugs)

    repos:list[Repository] = []
    for slug in repository_slugs:
        r:Repository = g.get_repo(slug)
        if not exclude_archived or (exclude_archived and r.archived is False):
            repos.append(r)

    logging.info(f' (repository) found [{len(repos)}] repos from slugs', slugs=repository_slugs)
    return repos
