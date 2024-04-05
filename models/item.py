import json
from typing import TypeVar
from log.logger import logging
from utils.decorator import timer

# type of the source object, could be dict, a class etc
T = TypeVar('T')
# type of each fields values, this can be any standard type
V = TypeVar('V')


class Item:
    """Simple container item to hold key data from other classes to reduce complexity latest"""
    _type: type = None

    @timer
    def __init__(self, data:T, attrs_to_use:list[str] = []) -> None:
        self._setup(data, attrs_to_use)

    @timer
    def _setup(self, data:T, attrs_to_use:list[str] = []) -> None:
        """Use the data and filters passed to setup this item to contain correct attributes based on the source"""
        self._type = type(data)
        logging.info('type of data converting to Item', type=self._type, attrs_to_use=attrs_to_use)

        items = data.__dict__.items() if type(data) is not dict else data.items()
        for key, v in items:
            logging.debug('getting property', property=key)
            # check if its a standard type
            # TODO - better way of doing this?
            value:V = None
            baseInstance = isinstance(v, (int, float, str, bool, complex, list, dict, tuple, range, type(None)) )
            keep:bool = (len(attrs_to_use) ==0 or key in attrs_to_use)
            keep_underscore: bool = (key[0] == '_' and key[1:] in attrs_to_use)

            logging.debug('property criteria', baseInstance=baseInstance, keep=keep, keep_underscore=keep_underscore)
            if baseInstance:
                value = v
            elif hasattr(v, 'value'):
                value = getattr(v, 'value')

            if keep:
                self.__setattr__(key, value)
            elif keep_underscore:
                self.__setattr__(key[1:], value)

        logging.debug('converted', type=self._type, item=self.dict())

    ##############
    # display related
    ##############
    def __repr__(self) -> str:
        return json.dumps(self.dict(), indent=4, sort_keys=True, default=str)


    ##############
    # public get / set / delete versions
    ##############
    @timer
    def get(self, name:str) -> V | None:
        """Uses __getattribute__ but silences AttributeError if the attribute does not exist and retuns None instead."""
        try:
            return  self.__getattribute__(name)
        except AttributeError:
            logging.warn('failed to get value for property', property=name)
            return None

    @timer
    def set(self, name:str, value: V) -> None:
        self.__setattr__(name, value)

    @timer
    def delete(self, name:str) -> None:
        """Uses __delattr__ but silences AttributeError if the attribute does not exist and retuns None instead."""
        try:
            self.__delattr__(name)
        except AttributeError:
            logging.warn('failed to delete property', property=name)

    @timer
    def dict(self) -> dict[str, V]:
        """Use the built in __dict__ method"""
        return {k:v for k,v in self.__dict__.items()}


    @timer
    def rename(self, old:str, new:str) -> None:
        """Rename uses set and then delete to change the values.

        Note: This will overwrite any existing item in attribute whose key matches `old`

        """
        value = self.get(old)
        logging.info('renaming property', old=old, new=new, val=value)
        self.set(new, value)

        self.delete(old)
        logging.debug('renamed property', old=old, new=new, item=self.dict())
