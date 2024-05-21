import os
import pytest
from pprint import pp

from github import Github
from github.Repository import Repository
from app.data.github.local.map import Local

from faker import Faker
from fake.github.repository import FakeGithubRepositoryProvider
fake = Faker()
fake.add_provider(FakeGithubRepositoryProvider)


def test_data_github_repository_converts():
    """Simple test to see a random repo run converts over to a dict version"""
    source:Repository = fake.github_repository()
    data:dict = Local(source)
    assert source.id == data.get('id')
    assert source.name == data.get('name')
    assert source.full_name == data.get('full_name')


@pytest.mark.skipif(os.environ.get('GITHUB_TEST_TOKEN', 0) == 0, reason='Requires github token to run')
def test_data_github_repository_converts_from_real():
    """Test the a real repository is converted over ok"""

    g:Github = Github(os.environ.get('GITHUB_TEST_TOKEN'))
    source:Repository = g.get_repo("ministryofjustice/opg-github-actions")
    data:dict = Local(source)
    assert source.full_name == data.get('full_name')
    assert source.get_hooks().totalCount == data.get('webhooks_count')
