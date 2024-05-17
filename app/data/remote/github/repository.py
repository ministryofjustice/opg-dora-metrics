from github import Github
from github.Repository import Repository
from app.log.logger import logging

def repo(g:Github, slug:str) -> Repository:
    """Return a repository based on the slug"""
    logging.debug('getting repository', slug=slug)
    return g.get_repo(slug)

