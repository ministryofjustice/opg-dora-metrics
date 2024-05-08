import argparse
import os
import json
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from typing import Any

from aws.client import client
from aws.cloudwatch import health_check_metrics, heath_check_metric_stats
from log.logger import logging
from pprint import pp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--service', help='Name of the service - this is added into the datapoints to help merging later', required=True)
    args = parser.parse_args()

    now:datetime = datetime.now(timezone.utc)
    end:datetime = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start:datetime = end - relativedelta(days=1)

    cw = client('cloudwatch', 'us-east-1')
    metrics = health_check_metrics(cw)
    # make a call for every
    data:list[dict[str,Any]] = heath_check_metric_stats(cw, metrics, start, end)
    service:str = args.service
    # inject the service name
    for item in data:
        item['Service'] = service
    # dir to output to
    dir:str = './outputs/service_uptime_daily/'
    os.makedirs(dir, exist_ok=True)
    # write raw json to file
    rawfile:str = f'{dir}./{service}-{start.date()}.json'
    with open(rawfile, 'w+') as f:
        json.dump(data, f, sort_keys=True, indent=2, default=str)

if __name__ == "__main__":
    main()
