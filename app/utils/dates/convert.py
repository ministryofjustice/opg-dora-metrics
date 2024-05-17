from datetime import datetime, date, timezone
from dateutil.relativedelta import relativedelta
from app.decorator import timer

@timer
def to_datetime(original:str|date, format='%Y-%m') -> datetime:
    """Convert a string or date to a datetime"""
    assert isinstance(original, (str, date))    
    out:datetime = None
    if type(original) is str:
        out = datetime.strptime(original, format)
    elif type(original) is date:
        out = datetime(year=original.year, month=original.month, day=original.day, 
                       hour=0, minute=0, second=0, tzinfo=timezone.utc)
    return out
    
@timer
def to_date(original:str|datetime, format='%Y-%m') -> date:
    """Convert a string or datetime to a date"""
    assert isinstance(original, (str, datetime))    
    out:date = None
    if type(original) is str:
        out = datetime.strptime(original, format).date()
    elif type(original) is datetime:
        out = original.replace(tzinfo=timezone.utc).date()
    return out
    
