from typing import Any, TypeVar, Callable
from pprint import pp

from github.GithubObject import GithubObject, Attribute, _ValuedAttribute


S = TypeVar('S', bound=GithubObject)
G = TypeVar('G', bound=GithubObject)
V = TypeVar('V', bound=GithubObject)


def attach_property(source:G, property:str, value:V|list[V]) -> None:
    """Attach the class to the attribute attr with value"""
    attr = _ValuedAttribute(value)
    setattr(source, property, attr)
