from pprint import pp

from faker import Faker
from faker.providers import BaseProvider
fake = Faker()

class FakeGithubDataArtifactProvider(BaseProvider):
    """Generate fake github data artifact"""

    def githubdata_artifacts(self,
                             count:int = 1,
                             lower_date:str='-3m',
                             upper_date:str='-1m',
                             real_values:dict={}) -> list[dict]:
        """many fake artifacts"""
        return [self.githubdata_artifact(lower_date=lower_date, upper_date=upper_date, real_values=real_values) for i in range(0,count)]

    def githubdata_artifact(self,
                            lower_date:str='-3m',
                            upper_date:str='-1m',
                            real_values:dict={}) -> dict:
        """Generate a artifact"""
        created:str = fake.date_time_between(start_date=lower_date, end_date=upper_date).isoformat()
        attributes:dict = {
            'id': fake.random_number(),
            'created_at': created,
            'name': fake.word(),
            'archive_download_url': fake.uri(),
            'date': created,
        }
        if len(real_values.keys()) > 0:
            attributes.update(real_values)
        return attributes
