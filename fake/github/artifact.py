from pprint import pp

from github.Artifact import Artifact

from faker import Faker
from faker.providers import BaseProvider
fake = Faker()

class FakeGithubArtifactProvider(BaseProvider):
    """Generate fake github item"""
    def github_artifact(self, 
                        lower_date:str='-3m',
                        upper_date:str='-1m',
                        real_values:dict={}) -> Artifact:
        """Generate an artifact"""

        created:str = fake.date_between(start_date=lower_date, end_date=upper_date).isoformat()
        attributes:dict = {
            'id': fake.random_number(),
            'created_at': created,            
            'name': fake.word(),
            'archive_download_url': fake.uri(),
        }      
        if len(real_values.keys()) > 0:
            attributes.update(real_values)
        artifact:Artifact = Artifact(requester=None, headers={}, completed=True, attributes=attributes)
        return artifact