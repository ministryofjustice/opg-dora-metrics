from typing import Any

from models.base import DictionaryGetterSetter

from pprint import pp

class Item(DictionaryGetterSetter):
    """Simple container item to hold key data from other classes to reduce complexity latest"""

    def __init__(self, data:Any, filter:list[str] = None) -> None:
        """"""
        items = data.__dict__.items() if type(data) is not dict else data.items()
        for key, v in items:
            # check if its a standard type
            # TODO - better way of doing this?
            baseInstance = isinstance(v, (int, float, str, bool, complex, list, dict, tuple, range, type(None)) )
            value:Any = None
            if baseInstance:
                value = v
            elif hasattr(v, 'value'):
                value = getattr(v, 'value')

            if filter is None or key in filter:
                self.set(key, value)
            elif key[0] == '_' and key[1:] in filter:
                self.set(key[1:], value)
