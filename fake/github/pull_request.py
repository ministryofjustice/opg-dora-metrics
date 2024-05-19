from datetime import date
from pprint import pp

from github.PullRequest import PullRequest

from faker import Faker
from faker.providers import BaseProvider
fake = Faker()

class FakeGithubPullRequestProvider(BaseProvider):
    """Generate fake github item"""
    def github_pull_requests(self,
                             count:int = 1,
                             closed:bool = None,
                             branch:str = 'main',
                             lower_date:str|date='-3m',
                             upper_date:str|date='-1m',
                             real_values:dict={}) -> list[PullRequest]:
        """Generate multiple fakes"""
        return [self.github_pull_request(closed=closed, branch=branch, lower_date=lower_date, upper_date=upper_date, real_values=real_values) for i in range(0, count)]

    def github_pull_request(self,
                            closed:bool = None,
                            branch:str = 'main',
                            lower_date:str|date='-3m',
                            upper_date:str|date='-1m',
                            real_values:dict={}) -> PullRequest:
        """Generate an pull_request"""

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
        pull_request:PullRequest = PullRequest(requester=None, headers={}, completed=True, attributes=attributes)
        return pull_request
