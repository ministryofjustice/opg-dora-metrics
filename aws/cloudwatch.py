import boto3
from datetime import datetime
from typing import Any

from utils.decorator import timer
from log.logger import logging

from pprint import pp

_metric:str = 'HealthCheckPercentageHealthy'

@timer
def health_check_metrics(client) -> list[dict[str,str]]:
    """Return a list of all health check metrics and the matching values"""
    logging.debug('getting list of health check metrics')
    paginator = client.get_paginator('list_metrics')
    metrics:list[dict[str,str]] = []
    for response in paginator.paginate(MetricName=_metric):
        for m in response['Metrics']:
            metrics.append(m)
    logging.debug('list of health check metrics found', metrics=metrics)
    return metrics

@timer
def _just_dimensions(metric_list:list[dict[str,str]]) -> list[dict[str,str]]:
    """Return only the Dimensions section of the metric list"""
    dimensions:list[dict[str,str]] = []
    for metric in metric_list:
        for d in metric['Dimensions']:
            dimensions.append(d)
    return dimensions

@timer
def heath_check_metric_stats(client,
                             metrics:list[dict[str,str]],
                             start:datetime,
                             end:datetime,
                             period:int = 60,
                             unit:str = 'Percent',
                             stats:list[str] = ['Average']
                             ) -> list[dict[str,Any]]:
    """Call the AWS api to get datapoints for the healthchecks between the dates passed"""
    logging.info('getting health check stats', start=start, end=end, period=period, unit=unit, stats=stats)

    data_points:list[dict[str,Any]] = []
    namespace:str = 'AWS/Route53'
    dimensions:list[dict[str,str]] = _just_dimensions(metrics)

    logging.info('health check metrics found', found=len(metrics))
    if len(dimensions) > 30:
        logging.error('can only use 30 dimensions, truncating')
        dimensions = dimensions[0:29]

    response = client.get_metric_statistics(
        Namespace=namespace,
        MetricName=_metric,
        Period=period,
        StartTime=start,
        EndTime=end,
        Statistics=stats,
        Unit=unit,
        Dimensions=dimensions,
    )
    # if theres an error code returned
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        logging.error('AWS API returned failure', response=response)
        raise Exception('Failed to get metrics data from AWS')
    else:
        data_points = response['Datapoints']
    logging.debug('datapoints found', start=start, end=end, period=period, unit=unit, stats=stats)
    logging.info('datapoints found', found=len(data_points))
    return data_points
