from pprint import pp

from github.WorkflowRun import WorkflowRun

from faker import Faker
from faker.providers import BaseProvider
fake = Faker()

class FakeGithubWorkflowRunProvider(BaseProvider):
    """Generate fake github item"""
    def github_workflow_run(self, 
                            success:bool = None,
                            branch:str = 'main',
                            lower_date:str='-3m',
                            upper_date:str='-1m',
                            real_values:dict={}) -> WorkflowRun:
        """Generate an workflow_run"""

        created:str = fake.date_between(start_date=lower_date, end_date=upper_date).isoformat()
        attributes:dict = {
            'id': fake.random_number(),
            'created_at': created,
            'conclusion': 'success' if success else 'failure',
            'head_branch': branch,
            'name': fake.word()
        }   
        if len(real_values.keys()) > 0:
            attributes.update(real_values)
        workflow_run:WorkflowRun = WorkflowRun(requester=None, headers={}, completed=True, attributes=attributes)
        return workflow_run