from github import Github
from github.Organization import Organization
from github.Team import Team
from github import Auth

def init(token:str=None, organisation_slug:str=None, team_slug:str=None ) -> tuple:
    """Generate github, org and team instances"""
    g:Github = Github(auth=Auth.Token(token)) if token is not None else Github()
    org:Organization = g.get_organization(organisation_slug) if organisation_slug is not None else None
    team:Team = org.get_team_by_slug(team_slug) if team_slug is not None else None
    return g, org, team
