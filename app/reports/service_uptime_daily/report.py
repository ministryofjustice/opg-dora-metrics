from datetime import datetime
from typing import Any
import json

def report(service:str, start:datetime, data:list[dict[str,Any]]) -> dict[str, Any]:
    """Generate dict of report data for daily uptime reports"""
    for item in data:
        item['Service'] = service

    name:str = f'{service}-{start.date()}.json'
    return {
        name: data
    }
