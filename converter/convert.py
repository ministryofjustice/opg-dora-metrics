import json
from typing import TypeVar, Any, Callable

from log.logger import logging
from utils.decorator import timer
from converter.meta import attributes

from pprint import pp

T = TypeVar('T')

##############
# exceptions
##############
class UnsupporterTypeForConversion(Exception):
    pass


class remapper:
    old:str
    new:str
    func:Callable[[Any], Any] = None
    def __init__(self, old:str, new:str, f:Callable[[Any], Any] = None) -> None:
        self.old = old
        self.new = new
        self.func = f


##############
#
##############
@timer
def _key(field:str, values:dict[str, Any]) -> str | None:
    """Get correct key name, looking for _ prefixes"""
    if values.get(field, None) != None:
        return field
    elif values.get(f'_{field}', None) != None:
        return f'_{field}'
    return None

@timer
def _value(v:Any) -> Any | None:
    """Find the value for item passed. For certain types, this might be a sub call (.value etc)"""
    baseInstance = isinstance(v, (int, float, str, bool, complex, list, dict, tuple, range, type(None)) )
    if baseInstance:
        return v
    elif hasattr(v, 'value'):
        return getattr(v, 'value')
    return None
##############
#
##############
@timer
def remap_values(item:dict[str,Any], old_key:str, new_key:str, new_value:Callable[[Any], Any] = None) -> dict[str,Any]:
    """Allows renaming and changing the value of the new field at the same time"""
    value:Any = item.get(old_key, None)
    # replace the value
    if new_value is not None:
        logging.debug('replacing value via function', old_key=old_key, new_key=new_key, new_value=new_value)
        value:Any = new_value(value)
    # set the value
    item[new_key] = value
    del item[old_key]
    logging.info('renampped values', old_key=old_key, new_key=new_key, result=item)
    return item

@timer
def to(input:T, attrs:list[str] = [], remap:list[remapper] = None ) -> dict[str, Any]:
    """Take the required input and convert to a dictionary with matching fields"""
    t = type(input)
    fields:list[str] = []
    converted:dict[str, Any] = {}
    # look at attributes passed or the meta information
    # to find correct fields to use
    if len(attrs) > 0:
        fields = attrs
        logging.debug('converting using passed attrs', fields=fields)
    elif len(attributes(t)) > 0:
        fields = attributes(t)
        logging.debug('converting using known attrs from meta', fields=fields)
    else:
        logging.warn('unsupported type', type=t)
        raise UnsupporterTypeForConversion(f'Type [{t}] not supported for conversion')

    # get the values as a dict
    values:dict[str, Any] = input if t is dict else input.__dict__
    # loop over the fields we want ant fetch their values
    for field in fields:
        key:str = _key(field, values)
        value:Any = _value(values.get(key))
        converted[field] = value

    # look for remapping
    if remap is not None:
        logging.debug('remapping fields', remap=remap)
        for rmp in remap:
            converted = remap_values(converted,
                                    old_key=rmp.old,
                                    new_key=rmp.new,
                                    new_value=rmp.func)
    # add converstion history
    converted['_source'] = t

    logging.info('converted data to dict', type=t, result=converted)
    return converted
