from pprint import pp

from github.Team import Team

from faker import Faker
from faker.providers import BaseProvider
fake = Faker()

class FakeGithubTeamProvider(BaseProvider):
    """Generate fake github team"""

    def github_teams(self, count:int = 1, real_values:dict={}) -> list[Team]:
        """many fake teams"""
        return [self.github_team(real_values=real_values) for i in range(0, count)]
    
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