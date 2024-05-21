import os
import pytest
from pprint import pp

from github.WorkflowRun import WorkflowRun
from app.data.github.local.map import Local

from faker import Faker
from fake.github.workflow_run import FakeGithubWorkflowRunProvider
fake = Faker()
fake.add_provider(FakeGithubWorkflowRunProvider)


def test_data_github_workflow_run_converts():
    """Simple test to see a random workflow run converts over to a dict version"""

    source:WorkflowRun = fake.github_workflow_run()
    data:dict = Local(source)
    assert source.id == data.get('id')
    assert source.name == data.get('name')
