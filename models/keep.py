from typing import Self
from datetime import datetime
from enum import Enum

from github.Repository import Repository
from github.WorkflowRun import WorkflowRun
from github.PullRequest import PullRequest

from pprint import pp

class Keep(Enum):
    """Keep is an enum that determines which fields should be kept from each class we are using in stats

    Also allows use with faker to create versions of date with mocked attrs
    """
    # github
    ID          = ('id', [PullRequest, WorkflowRun, Repository], int)
    ## repos
    FULL_NAME   = ('full_name', [Repository], str)
    ## pull requests
    TITLE       = ('title', [PullRequest], str)
    MERGED_AT   = ('merged_at', [PullRequest], datetime)
    STATE       = ('state', [PullRequest],  list, ['closed', 'open'])
    ## workflow runs
    NAME        = ('name', [WorkflowRun], str)
    CREATED_AT  = ('created_at', [WorkflowRun], datetime)
    CONCLUSION  = ('conclusion', [WorkflowRun],  list, ['success', 'failure'])

    def __new__(cls, attr:str, models:list, value_type, choices = None) -> Self:
        obj = object.__new__(cls)
        obj._value_ = attr
        obj.models = models
        obj.value_type = value_type
        obj.choices = choices
        return obj



def specs(cls) -> list[dict]:
    """Return all the enum details for class"""
    found:list = []
    for e in Keep:
        if cls in e.models:
            found.append({
                'attr': e._value_,
                'value_type': e.value_type,
                'choices': e.choices,
            })
    return found

def spec(cls, attr:str) -> dict:
    """Return a specifc enaum detail as a dict"""
    all = specs(cls)
    for s in all:
        if s.get('attr', None) == attr:
            return s
    return {}

def attrs(cls) -> list[str]:
    """Return only the attribute names for the enums attached to this class"""
    all = specs(cls)
    return [v.get('attr') for v in all]
