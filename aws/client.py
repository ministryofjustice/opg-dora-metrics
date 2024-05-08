import boto3

from utils.decorator import timer

@timer
def client(type:str, role:str, region:str):
    """Return a client that will use env vars for authentication"""
    sts = boto3.client('sts')
    session = sts.assume_role(RoleArn=role, RoleSessionName="dora-metrics", DurationSeconds=900)
    return boto3.client(
        type,
        aws_access_key_id=session['Credentials']['AccessKeyId'],
        aws_secret_access_key=session['Credentials']['SecretAccessKey'],
        aws_session_token=session['Credentials']['SessionToken'],
        region_name=region)
