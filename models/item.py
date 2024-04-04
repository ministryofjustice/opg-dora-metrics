import sys
import json
from typing import TypeVar
from log.logger import logging

# type of the source object, could be dict, a class etc
T = TypeVar('T')
# type of each fields values, this can be any standard type
V = TypeVar('V')



class Item:
    """Simple container item to hold key data from other classes to reduce complexity latest"""
    _fields: list[str] = []
    _type: type = None

    def __init__(self, data:T, filter:list[str] = None) -> None:
        logging.debug('start')
        self._fields = []
        self._type = type(data)
        logging.info('type of data converting to Item', type=self._type)
        self.__setup__(data, filter)
        logging.debug('end')

    def __setup__(self, data:T, filter:list[str] = None) -> None:
        """Use the data and filters passed to setup this item to contain correct attributes based on the source"""
        logging.debug('start')
        items = data.__dict__.items() if type(data) is not dict else data.items()
        for key, v in items:
            logging.debug('getting property', property=key)
            # check if its a standard type
            # TODO - better way of doing this?
            value:V = None
            baseInstance = isinstance(v, (int, float, str, bool, complex, list, dict, tuple, range, type(None)) )
            keep:bool = (filter is None or key in filter)
            keep_underscore: bool = (key[0] == '_' and key[1:] in filter)

            logging.debug('property criteria', baseInstance=baseInstance, keep=keep, keep_underscore=keep_underscore)
            if baseInstance:
                value = v
            elif hasattr(v, 'value'):
                value = getattr(v, 'value')

            if keep:
                self._fields.append(key)
                self.__setattr__(key, value)
            elif keep_underscore:
                self._fields.append(key[1:])
                self.__setattr__(key[1:], value)

        logging.debug('end')

    ##############
    # display related
    ##############
    def __repr__(self) -> str:
        return json.dumps(self.__dict__(), indent=4, sort_keys=True, default=str)

    def __dict__(self) -> dict[str, V]:
        data:dict[str, V] = {}
        for f in self._fields:
            data[f] = self.__getattribute__(f)
        return data

    ##############
    # public get / set / delete versions
    ##############
    def get(self, name:str) -> V | None:
        try:
            return  self.__getattribute__(name)
        except:
            logging.warn('failed to get value for property', property=name)
            return None

    def set(self, name:str, value: V) -> None:
        self.__setattr__(name, value)

    def delete(self, name:str) -> None:
        self.__delattr__(name)

    def dict(self) -> dict[str, V]:
        return self.__dict__()

    def rename(self, old:str, new:str) -> None:
        logging.info('renaming property', old=old, new=new)
        self.set(new, self.get(old))
        self.delete(old)
