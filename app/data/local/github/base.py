from typing import Any, TypeVar, Callable
from types import FunctionType
from github.GithubObject import GithubObject, _ValuedAttribute, Attribute
from app.log.logger import logging
from app.decorator import timer

G = TypeVar('G', bound=GithubObject)


@timer
def DataMap(source:G, map:dict[str, Callable|None]) -> dict[str, Any]:
    """Use a map of attributes passed to generate a dict of data
    Key of the dict if the field name, if the value is a function that is called,
    otherwise a direct mapp to attribute is tried
    """
    logging.debug('Data mapping', source=source)
    raw:dict[str, Any] = {}

    if source is not None and getattr(source, '__dict__') is not None:
        source_data:dict[str, Any] = vars(source)
        raw:dict[str, Any] = source_data['_rawData']

    result: dict = {}
    for attr, f in map.items():
        value:Any = None
        is_func:bool = isinstance(f, FunctionType)
        if is_func:
            try:
                value = f(source)
            except:
                pass
        else:
            value = raw.get(attr, None)
        result[attr] = value

    result['__class__'] = source.__class__.__name__
    return result
