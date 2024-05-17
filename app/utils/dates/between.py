from datetime import datetime, date, timezone
from app.decorator import timer

@timer
def between(test:datetime|None, lower:datetime, upper:datetime) -> bool:
    """Confirms if datetime is between the date range and not None"""
    return (test is not None) and (test >= lower and test <= upper)