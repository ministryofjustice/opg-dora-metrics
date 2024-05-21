import os
import pytest
from pprint import pp

from github import Github
from github.Team import Team
from app.data.github.local.map import Local

from faker import Faker
from fake.github.team import FakeGithubTeamProvider
fake = Faker()
fake.add_provider(FakeGithubTeamProvider)


def test_data_github_team_converts():
    """Simple test to see a random team converts over to a dict version"""

    team:Team = fake.github_team()
    data:dict = Local(team)
    assert team.id == data.get('id')
    assert team.slug == data.get('slug')
