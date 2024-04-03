import logging
from typing import Any, Self
import json

from github.GithubObject import GithubObject

from pprint import pp

class Simple:
    """Simple is used to store only the import information we want to report on from much larger classes.

    For example, the github.Repository class contains dozens of methods and properties but we only report
    on the name. You can then use this class to create a simplified version

    """
    _source:Any = None
    _properties:dict[str, Any] = {}

    def __init__(self, **kwargs) -> None:
        self._properties = {}
        for key, value in kwargs.items():
            self.set(key, value)

    def __repr__(self) -> str:
        """Output a json string version of this objects vars"""
        return json.dumps(self._properties, indent=4, sort_keys=True, default=str)

    def __getattr__(self, name:str) -> Any|None:
        return self.get(name)

    def __delattr__(self, name:str) -> None:
       self.delete(name)

    def __delitem__(self, name:str) -> None:
        self.delete(name)

    def get(self, key:str) -> Any|None:
        """Return the value present at Key, default to None"""
        return self._properties.get(key, None)

    def set(self, key:str, value:Any) -> None:
        """Set a value for the key"""
        self._properties.setdefault(key, value)
        self._properties[key] = value

    def delete(self, key:str) -> None:
        self._properties.pop(key)

    @staticmethod
    def instance(source:Any, properties:list) -> Self:
        """Create a new Simple instance based on a different data source and a series of property names."""

        logging.debug("[models.Simple] creating instance from source object")
        _vars: dict[str, Any] = dict({v: None for v in properties})

        # if this is a GithubObject, then handle it differently
        #   - trim _ from the start of keys
        #   - use the .value property of the v
        if isinstance(source, GithubObject):
            for k, v in vars(source).items():
                k = k[1:]
                if k in properties:
                    _vars[k] = v.value
        elif isinstance(source, dict):
            for k, v in source.items():
                if k in properties:
                    _vars[k] = v
        else:
            for k, v in vars(source).items():
                if k in properties:
                    _vars[k] = v
        # track the source type for this data
        _vars['_type'] = type(source)
        return Simple(**_vars)
