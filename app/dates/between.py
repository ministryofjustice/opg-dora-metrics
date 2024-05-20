from datetime import datetime, date, timezone

def between(test:datetime|None, lower:datetime, upper:datetime) -> bool:
    """Confirms if datetime is between the date range and not None"""
    if test is not None:
        test = test.replace(tzinfo=timezone.utc)
    lower = lower.replace(tzinfo=timezone.utc)
    upper = upper.replace(tzinfo=timezone.utc)
    return (test is not None) and (test >= lower and test <= upper)
