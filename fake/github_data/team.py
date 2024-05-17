from pprint import pp
from faker import Faker
from faker.providers import BaseProvider
fake = Faker()

class FakeGithubDataTeamProvider(BaseProvider):
    """Generate fake github data team"""

    def githubdata_teams(self, count:int = 1, real_values:dict={}) -> list[dict]:
        """many fake teams"""
        return [self.githubdata_team(real_values=real_values) for i in range(0, count)]

    def githubdata_team(self, real_values:dict={}) -> dict:
        """Generate a team"""
        name:str = fake.slug()
        attributes:dict = {
            'name': name,
            'id': fake.random_number(),
            'slug': name,
            'parent': {
                'name': name,
                'id': fake.random_number(),
                'slug': name,
            }
        }
        if len(real_values.keys()) > 0:
            attributes.update(real_values)
        return attributes
