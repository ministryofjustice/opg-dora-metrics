import os
from datetime import datetime, timezone, timedelta

def start() -> str:
    """Returns a timestamp for the current time

    Returns:
    str: UTC based ISO 6801 timestamp
    """
    return datetime.now(timezone.utc).isoformat()

def stop() -> str:
    """Returns a timestamp for the current time

    Wrapper for start() for nicer syntax.

    Returns:
    str: UTC based ISO 6801 timestamp
    """
    return start()


def duration(start: str, stop: str) -> int:
    """Returns number of seconds between start and stop timestamps

    Parameters:
    start (str): Starting timestamp (UTC ISO 6801)
    stop (str): End timestamp (UTC ISO 6801)

    Returns:
    int: Rounded number of seconds between the timestamps
    """
    data:dict = durations(start, stop)
    seconds = data.get('seconds', 0.0)
    return round(seconds)

def durations(start: str, stop: str) -> dict:
    """Returns number of seconds between start and stop timestamps as decimal versions

    Parameters:
    start (str): Starting timestamp (UTC ISO 6801)
    stop (str): End timestamp (UTC ISO 6801)

    Returns:
    dict (str: float): Contains duration in milliseconds, seconds, minutes and hours
    """
    start_ts = datetime.fromisoformat(start)
    stop_ts = datetime.fromisoformat(stop)
    diff = stop_ts - start_ts
    return {
        'milliseconds': diff / timedelta(milliseconds=1),
        'seconds': diff / timedelta(seconds=1),
        'minutes': diff / timedelta(minutes=1),
        'hours': diff / timedelta(hours=1),
    }
