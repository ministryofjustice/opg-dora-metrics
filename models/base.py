from typing import Any
import json

from pprint import pp

class DictionaryGetterSetter:
    """Generic model"""
    _data: dict[str, Any] = {}

    def __init__(self) -> None:
        self.reset()

    @classmethod
    def reset(cls) -> None:
        cls._data = {}

    ##############
    # Generic property getters / setters / deletes
    # that will use data as a store instead
    ##############
    def __getattr__(self, name:str) -> Any | None:
        return self._data.get(name, None)

    def __setattr__(self, name:str, value:Any) -> None:
        self._data[name] = value

    def __delattr__(self, name:str) -> None:
        self._data.pop(name)

    def __delitem__(self, name:str) -> None:
        self.__delattr__(name)

    ##############
    # display related
    ##############
    def __repr__(self) -> str:
        return json.dumps(self._data, indent=4, sort_keys=True, default=str)

    def __dict__(self) -> dict[str, Any]:
        return self._data

    ##############
    # public get / set / delete versions
    ##############
    def get(self, name:str) -> Any | None:
        return  self.__getattr__(name)

    def set(self, name:str, value: Any) -> None:
        self.__setattr__(name, value)

    def delete(self, name:str) -> None:
        self.__delattr__(name)

    def dict(self) -> dict[str, Any]:
        return self.__dict__()

    def rename(self, old:str, new:str) -> None:
        self.set(new, self.get(old))
        self.delete(old)
