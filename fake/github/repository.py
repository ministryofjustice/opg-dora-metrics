from pprint import pp

from github.Repository import Repository

from faker import Faker
from faker.providers import BaseProvider
fake = Faker()

class FakeGithubRepositoryProvider(BaseProvider):
    """Generate fake github item"""
    def github_repository(self, 
                          branch:str='main',
                          real_values:dict={}) -> Repository:
        """Generate an repository"""

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
        repository:Repository = Repository(requester=None, headers={}, completed=True, attributes=attributes)
        return repository