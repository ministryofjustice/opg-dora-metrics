from pprint import pp

from github.Artifact import Artifact
from github.WorkflowRun import WorkflowRun
from github.GithubObject import Attribute

from faker import Faker
from faker.providers import BaseProvider
fake = Faker()

class FakeGithubArtifactProvider(BaseProvider):
    """Generate fake github item"""
    def github_artifacts(self, 
                         count:int = 1,
                         lower_date:str='-3m',
                         upper_date:str='-1m',
                         real_values:dict={}) -> list[Artifact]:
        """Generate multiple artifacts"""
        return [self.github_artifact(lower_date=lower_date, upper_date=upper_date, real_values=real_values) for i in range(0,count)]

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
    