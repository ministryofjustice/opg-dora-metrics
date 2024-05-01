from faker import Faker
from typing import Any, TypeVar
from github.GithubObject import GithubObject, CompletableGithubObject
from converter.meta import _PropertyTypes, properties, attributes

############################
# Internal functions to return faker data
############################
fake = Faker()

def _int(args:dict) -> int:
    return fake.random_number()

def _str(args:dict) -> str:
    return fake.sentence(nb_words=4) + args.get('name', '')

def _state(args:dict) -> str:
    return 'open' if args.get('open', False) else 'closed'

def _conculsion(args:dict) -> str:
    return 'failure' if args.get('failure', False) else 'success'

def _datetime(args:dict) -> str:
    s = args.get('start', '-2y')
    e = args.get('end', '-1m')
    return fake.date_between(start_date=s, end_date=e).isoformat()

############################
# generator class
############################
G = TypeVar('G', GithubObject, CompletableGithubObject)

class faux:
    """Faker generation class for models being used in the app"""
    # map the property types to lamdas for generation of data
    _funcMap:dict = {
        _PropertyTypes.INT.name: _int,
        _PropertyTypes.STR.name: _str,
        _PropertyTypes.DATETIME.name: _datetime,
        _PropertyTypes.STATE.name: _state ,
        _PropertyTypes.CONCLUSION.name: _conculsion,
    }

    @staticmethod
    def _attrs(cls, **kwargs):
        """Generate a skeleton of faker data for the class (cls) passed"""
        attrs:dict[str, Any] = {}
        props = properties(cls)
        names = attributes(cls)
        for p in props:
            key = p.get('attribute')
            funcType = p.get('t').name
            func = faux._funcMap[funcType]
            res = func(kwargs)
            attrs[key] = res

        # overwrite any real data that was passed along in kwargs
        for k, v in kwargs.items():
            if k in names:
                attrs[k] = v
        return attrs

    @staticmethod
    def New(G, **kwargs) -> G:
        """Create a new instance of type G and handle its setup with attrs"""
        attrs = faux._attrs(G, **kwargs)
        return G(requester=None, headers={}, completed=True, attributes=attrs)
