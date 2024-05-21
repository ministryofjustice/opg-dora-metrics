import os
import pytest
from pprint import pp

from app.data.local.github.map import RepositoryBaselineComplianceAttributes
from app.data.local.standards.repository_standards_compliance import repository_standards

from faker import Faker
from fake.github_data.repository import FakeGithubDataRepositoryProvider
fake = Faker()
fake.add_provider(FakeGithubDataRepositoryProvider)


def test_data_local_standards_repository_standards():
    """Simple test to make sure standards is triggering correctly"""

    source:dict = fake.githubdata_repository()
    # as by default faker doesnt set any compliance info, all shoud fail
    result:dict = repository_standards(source)
    assert False == result['status']['baseline']
    assert False == result['status']['extended']
    # now set one baseline item to be True, but should be overall false
    key = list(RepositoryBaselineComplianceAttributes.keys())[0]
    source[key] = True
    result:dict = repository_standards(source)
    assert False == result['status']['baseline']
    assert False == result['status']['extended']
    # now we change all baseline items to be true
    for k in RepositoryBaselineComplianceAttributes.keys():
        source[k] = True
    result:dict = repository_standards(source)
    assert True == result['status']['baseline']
    assert False == result['status']['extended']
