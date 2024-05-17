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
    logging.debug('Data mapping', source=source, map=map)

    source_data:dict[str, Any] = vars(source)
    raw:dict[str, Any] = source_data['_rawData']

    result: dict = {}
    for attr, f in map.items():
        value:Any = None
        try:
            if isinstance(f, FunctionType):
                logging.debug(f'mapping [{attr}] as a function', f=f)
                value = f(source)
            else:
                logging.debug(f'mapping [{attr}] as an attribute')
                value = raw.get(attr, None)
        except Exception as e:
            logging.debug(f'failed to map data', attr=attr, exception=e)
            value = None
        logging.debug(f'mapped [{attr}] to [{value}]')
        result[attr] = value

    return result