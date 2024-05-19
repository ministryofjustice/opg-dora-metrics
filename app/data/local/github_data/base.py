from typing import Any, TypeVar, Callable
from types import FunctionType
from github.GithubObject import GithubObject, _ValuedAttribute, Attribute
from app.log.logger import logging
from app.decorator import timer

G = TypeVar('G', bound=GithubObject)

__cache__:dict = {}
WITH_CACHE:bool = False
# WITH_CACHE:bool = True

@timer
def DataMap(source:G, map:dict[str, Callable|None]) -> dict[str, Any]:
    """Use a map of attributes passed to generate a dict of data
    Key of the dict if the field name, if the value is a function that is called,
    otherwise a direct mapp to attribute is tried
    """
    logging.debug('Data mapping', source=source, map=map)
    raw:dict[str, Any] = {}
    # caching
    source_key:str = f'{source.__class__.__name__}:{source.id}'

    if source is not None and getattr(source, '__dict__') is not None:
        source_data:dict[str, Any] = vars(source)
        raw:dict[str, Any] = source_data['_rawData']

    result: dict = {}
    for attr, f in map.items():
        value:Any = None
        cache_key:str = f'{source_key}:{attr}'
        is_cached:bool = cache_key in __cache__.keys()
        is_func:bool = isinstance(f, FunctionType)
        if WITH_CACHE and is_cached:
            value = __cache__[cache_key]
            logging.debug(f'CACHED! [{attr}] to [{value}] [cached:{is_cached}]', is_function=is_func, f=f, cache_key=cache_key)
        elif is_func:
            try:
                value = f(source)
            except:
                pass
        else:
            value = raw.get(attr, None)
        # cache the result
        if WITH_CACHE:
            __cache__[cache_key] = value
        logging.debug(f'mapped [{attr}] to [{value}] [cached:{is_cached}]', is_function=is_func, f=f, cache_key=cache_key)
        result[attr] = value

    result['__class__'] = source.__class__.__name__
    return result
