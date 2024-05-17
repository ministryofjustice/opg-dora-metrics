from github import Github
from github.Repository import Repository


def repo(g:Github, slug:str) -> Repository:
    """Return a repository based on the slug"""
    return g.get_repo(slug)

