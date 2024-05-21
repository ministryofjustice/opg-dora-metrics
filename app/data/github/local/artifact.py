import os
import glob
import json
from zipfile import ZipFile
from tempfile import TemporaryDirectory
from datetime import datetime
import requests

from app.decorator import timer
from app.logger import logging

@timer
def __download__(url:str, download_to:str, token:str) -> None:
    """Download the url to a local file, assuming binary"""
    headers:dict[str,str] = {'Authorization': 'Bearer ' + token}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f'error downloading artifact [{url}]')
    with open(download_to, 'wb+') as f:
        f.write(response.content)

@timer
def __extract__(file:str, dir:str) -> None:
    """"""
    with ZipFile(file, 'r') as z:
        z.extractall(path=dir)
    os.remove(file)

@timer
def download(artifact:dict[str], token:str) -> list[dict[str]]:
    """Download an artifact to a temp location"""
    name:str = artifact['name']
    url:str = artifact['archive_download_url']
    date_str:str = datetime.fromisoformat(artifact['created_at']).date().strftime('%Y-%m-%d')
    content:list[dict] = []

    with TemporaryDirectory() as temp_dir:
        path:str = f'{temp_dir}/{name}-{date_str}.zip'
        logging.info('downloading artifact', url=artifact['archive_download_url'], to=path)
        __download__(url=url, download_to=path, token=token)
        __extract__(file=path, dir=temp_dir)
        # now loop over all the files and read them as json items
        for f in glob.glob(temp_dir + '/*.json'):
            with open(f) as file:
                content += json.load(file)
    return content

# @timer
# def _extract(self, dir:str, file:str):
#     """Extract this artifact file into the directory specified"""
#     logging.debug('extracting artifact', file=file, dir=dir)
#     with ZipFile(file, 'r') as z:
#         z.extractall(path=dir)
#     os.remove(file)

# @timer
# def _download(self, dir:str):
#     """Download this artifact to the dir passed"""
#     logging.debug('downloading artifact', url=self.artifact.archive_download_url, dir=dir, workflow=self.artifact.workflow_run.id, name=self.name)
#     filepath:str = f"{dir}/{self.name}-{self.artifact.created_at.date()}.zip"
#     headers:dict[str,str] = {'Authorization': 'Bearer ' + self.token}
#     response =  requests.get(self.artifact.archive_download_url, headers=headers)

#     if response.status_code != 200:
#         logging.error("Error downloading artifact", url=self.artifact.archive_download_url, name=self.name)
#         raise Exception(f"Error downloading artifact - {self.artifact.archive_download_url}")
#     with open(filepath, 'wb+') as f:
#         f.write(response.content)
#     return filepath
