import argparse
import os
import json
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from typing import Any
from app.reports.service_uptime_daily.report import report
from app.data.aws.client import client
from app.data.aws.cloudwatch import health_check_metrics, heath_check_metric_stats
from app.reports.writer import writer
from app.logger import logging
from pprint import pp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--service', help='Name of the service - this is added into the datapoints to help merging later', required=True)
    parser.add_argument('--role', help='role arn to assume for this command', required=True)
    args = parser.parse_args()

    logging.info(f'[Service Uptime Daily] starting')
    now:datetime = datetime.now(timezone.utc)
    end:datetime = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start:datetime = end - relativedelta(days=1)

    cw = client('cloudwatch', args.role, 'us-east-1')
    metrics:list[dict] = health_check_metrics(cw)
    # fetch the stats for each metrics
    data:list[dict[str,Any]] = heath_check_metric_stats(cw, metrics, start, end)
    report_data:dict = report(service=args.service, start=start, data=data)

    output_dir:str = './outputs/service_uptime_daily/'

    writer(report_data=report_data, output_dir=output_dir)
    logging.info(f'[Service Uptime Daily] complete')

if __name__ == "__main__":
    main()
