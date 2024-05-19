import os
import pytest
from unittest.mock import patch
from datetime import date,datetime,timezone
from pprint import pp
from dateutil.relativedelta import relativedelta
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.PullRequestPart import PullRequestPart

from faker import Faker
from fake.github import repository, pull_request
from fake.github.attach import attach_property
fake = Faker()
fake.add_provider(repository.FakeGithubRepositoryProvider)
fake.add_provider(pull_request.FakeGithubPullRequestProvider)


def test_fake_github_attach():
    """Test nested attachments"""
    repo:Repository = fake.github_repository(real_values={'full_name':'opg/test', 'name': 'test'})
    pr:PullRequest = fake.github_pull_request()
    base:PullRequestPart = fake.github_pull_request_base()

    attach_property(base, '_repo', repo)
    attach_property(pr, '_base', base)

    assert repo.id == base.repo.id
    assert repo.id == pr.base.repo.id
