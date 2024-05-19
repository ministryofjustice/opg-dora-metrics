from pprint import pp
from datetime import date
from github.WorkflowRun import WorkflowRun

from faker import Faker
from faker.providers import BaseProvider
fake = Faker()

class FakeGithubWorkflowRunProvider(BaseProvider):
    """Generate fake github item"""
    def github_workflow_runs(self, count:int = 1,
                             success:bool = None,
                             branch:str = 'main',
                             lower_date:str|date='-3m',
                             upper_date:str|date='-1m',
                             real_values:dict={}) -> list[WorkflowRun]:
        """"""
        return [self.github_workflow_run(success=success, branch=branch, lower_date=lower_date, upper_date=upper_date, real_values=real_values) for i in range(0, count)]

    def github_workflow_run(self,
                            success:bool = None,
                            branch:str = 'main',
                            lower_date:str|date='-3m',
                            upper_date:str|date='-1m',
                            real_values:dict={}) -> WorkflowRun:
        """Generate an workflow_run"""

        created:str = fake.date_time_between(start_date=lower_date, end_date=upper_date).isoformat()
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
