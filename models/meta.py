from typing import Any
from enum import Enum

from github.Repository import Repository
from github.WorkflowRun import WorkflowRun
from github.PullRequest import PullRequest



class _PropertyTypes(Enum):
    INT         = "int"
    STR         = "str"
    DATETIME    = "datetime"
    STATE       = "state"
    CONCLUSION  = "conclusion"


_model_properties:dict[Any, list[dict]] = {
    #### GITHUB ITEMS ####
    Repository: [
        {'attribute': 'id', 't': _PropertyTypes.INT },
        {'attribute': 'full_name', 't': _PropertyTypes.STR },
    ],
    WorkflowRun: [
        {'attribute': 'id', 't': _PropertyTypes.INT },
        {'attribute': 'name', 't': _PropertyTypes.STR },
        {'attribute': 'created_at', 't': _PropertyTypes.DATETIME },
        {'attribute': 'conclusion', 't': _PropertyTypes.CONCLUSION },
    ],
    PullRequest: [
        {'attribute': 'id', 't': _PropertyTypes.INT },
        {'attribute': 'number', 't': _PropertyTypes.INT },
        {'attribute': 'title', 't': _PropertyTypes.STR },
        {'attribute': 'merged_at', 't': _PropertyTypes.DATETIME },
        {'attribute': 'state', 't': _PropertyTypes.STATE },
    ],

}

def properties(cls) -> list[dict]:
    """get all attributes for this class we are interested in"""
    return _model_properties.get(cls, [])

def property(cls, field:str) -> dict:
    """get details for a single attribute"""
    all:list[dict] = properties(cls)
    for v in all:
        if v.get('attribute') == field:
            return v
    return {}

def attributes(cls) -> list[str]:
    all = properties(cls)
    return [v.get('attribute') for v in all]
