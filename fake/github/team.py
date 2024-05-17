from pprint import pp

from github.Team import Team

from faker import Faker
from faker.providers import BaseProvider
fake = Faker()

class FakeGithubTeamProvider(BaseProvider):
    """Generate fake github team"""
    def github_team(self, real_values:dict={}) -> Team:
        """Generate a team"""
        name:str = fake.slug()
        attributes:dict = {
            'name': name,
            'id': fake.random_number(),
            'slug': name
        }        
        if len(real_values.keys()) > 0:
            attributes.update(real_values)
        team:Team = Team(requester=None, headers={}, completed=True, attributes=attributes)
        
        return team