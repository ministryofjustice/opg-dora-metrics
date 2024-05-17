from typing import Any, TypeVar, Callable
from types import FunctionType
from pprint import pp
from github.GithubObject import GithubObject, _ValuedAttribute, Attribute

G = TypeVar('G', bound=GithubObject)


def DataMap(source:G, map:dict[str, Callable|None]) -> dict[str, Any]:
    """Use a map of attributes passed to generate a dict of data
    Key of the dict if the field name, if the value is a function that is called, 
    otherwise a direct mapp to attribute is tried
    """
    source_data:dict[str, Any] = vars(source)
    raw:dict[str, Any] = source_data['_rawData']

    result: dict = {}
    for attr, f in map.items():
        value:Any = None
        try:
            if isinstance(f, FunctionType):
                value = f(source)
            else:
                value = raw.get(attr, None)
        except Exception as e:
            value = None
        result[attr] = value

    return result