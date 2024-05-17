from datetime import date
from pprint import pp

from faker import Faker
from faker.providers import BaseProvider
fake = Faker()

class FakeGithubDataRepositoryProvider(BaseProvider):
    """Generate fake github data repository"""


    def githubdata_repository(self,
                              branch:str = 'main',
                              real_values:dict={}) -> dict:
        """Generate a repository"""
        name:str = fake.slug()
        attributes:dict = {
            'id': fake.random_number(),
            'name': name,
            'full_name': f'{fake.word()}/{name}',
            'branch': branch,
            'default_branch': branch,
            'url': fake.uri(),
        }
        if len(real_values.keys()) > 0:
            attributes.update(real_values)
        return attributes
