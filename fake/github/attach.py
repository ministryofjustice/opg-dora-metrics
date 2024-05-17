from typing import Any, TypeVar, Callable
from pprint import pp

from github.GithubObject import GithubObject, Attribute

G = TypeVar('G', bound=GithubObject)

def attach_property(source:G, attribute:str, value:G|list[G]):
    """Attach a workflow run to an artifact"""
    
    prop = Attribute
    prop.value = value
    setattr(source, attribute, prop)    

    return source