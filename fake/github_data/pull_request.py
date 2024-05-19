from datetime import date
from pprint import pp

from faker import Faker
from faker.providers import BaseProvider
fake = Faker()

class FakeGithubDataPullRequestProvider(BaseProvider):
    """Generate fake github data pull_request"""

    def githubdata_pull_requests(self,
                                 count:int = 1,
                                 closed:bool = None,
                                 branch:str = 'main',
                                 lower_date:str|date='-3m',
                                 upper_date:str|date='-1m',
                                 real_values:dict={}) -> list[dict]:
        """many fake pull_requests"""
        return [self.githubdata_pull_request(closed=closed, branch=branch, lower_date=lower_date, upper_date=upper_date, real_values=real_values) for i in range(0, count)]

    def githubdata_pull_request(self,
                                closed:bool = None,
                                branch:str = 'main',
                                lower_date:str|date='-3m',
                                upper_date:str|date='-1m',
                                real_values:dict={}) -> dict:
        """Generate a pull_request"""
        created:str = fake.date_time_between(start_date=lower_date, end_date=upper_date).isoformat()
        attributes:dict = {
            'id': fake.random_number(),
            'title': fake.word(),
            'state': 'closed' if closed else 'open',
            'base': branch,
            'number': fake.random_number(),
            'merged_at': created,
            'url': fake.uri(),
        }
        if len(real_values.keys()) > 0:
            attributes.update(real_values)
        return attributes
