import os
import pytest
from pprint import pp

from github.PullRequest import PullRequest
from app.data.local.github.map import Local

from faker import Faker
from fake.github.pull_request import FakeGithubPullRequestProvider
fake = Faker()
fake.add_provider(FakeGithubPullRequestProvider)


def test_data_github_pull_request_converts():
    """Simple test to see a random workflow run converts over to a dict version"""

    source:PullRequest = fake.github_pull_request()
    data:dict = Local(source)
    assert source.id == data.get('id')
    assert source.title == data.get('title')
