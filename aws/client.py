import boto3

from utils.decorator import timer

@timer
def client(type:str, region:str):
    """Return a client that will use env vars for authentication"""
    return boto3.client(type, region_name=region)
