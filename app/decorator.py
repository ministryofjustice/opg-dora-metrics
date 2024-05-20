from functools import wraps
import time
import json
from app.log.logger import logging


TRACK_DURATIONS:dict = {
    'enabled': False,
    'data': []
}

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        name:str = func.__name__
        if func.__module__:
            name = f'{func.__module__}.{func.__name__}'
        logging.debug('start', source_function=name, module=func.__module__)

        start = time.perf_counter()

        result = func(*args, **kwargs)

        end = time.perf_counter()
        duration = end - start

        if TRACK_DURATIONS['enabled']:
            TRACK_DURATIONS['data'].append({
                'duration': duration,
                'name': name,
                'args':args,
                'kwargs': kwargs,
            })

        logging.debug(f'end', duration=f'{duration:.4f} seconds', source_function=name)

        return result
    return wrapper
