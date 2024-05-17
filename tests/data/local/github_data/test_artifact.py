import os
import pytest
from pprint import pp

from github.Artifact import Artifact
from app.data.local.github_data.map import Local

from faker import Faker
from fake.github.artifact import FakeGithubArtifactProvider
fake = Faker()
fake.add_provider(FakeGithubArtifactProvider)


def test_data_github_arrtifact_converts():
    """Simple test to see a random artifact converts over to a dict version"""    

    source:Artifact = fake.github_artifact()
    data:dict = Local(source)

    assert source.id == data.get('id')
    assert source.name == data.get('name')