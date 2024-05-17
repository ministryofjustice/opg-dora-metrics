from functools import wraps
import time

from app.log.logger import logging

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

        logging.debug(f'end', duration=f'{duration:.4f} seconds', source_function=name)

        return result
    return wrapper
