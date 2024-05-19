import os
import pytest
from datetime import date, datetime
from pprint import pp
from dateutil.relativedelta import relativedelta
from app.utils.dates.convert import to_date
from app.utils.dates.ranges import date_range, Increment
from app.data.local.github_data.map import RepositoryBaselineComplianceAttributes
from app.reports.github_deployment_frequency.report import by_month, __merger__

from faker import Faker
from fake.github_data.repository import FakeGithubDataRepositoryProvider
from fake.github_data.workflow_run import FakeGithubDataWorkflowRunProvider
fake = Faker()
fake.add_provider(FakeGithubDataRepositoryProvider)
fake.add_provider(FakeGithubDataWorkflowRunProvider)


def test_reports_repository_deployments_by_month():
    """Simple test to make sure report generates"""

    end:date = datetime.now() - relativedelta(days=1)
    start:date = end - relativedelta(months=2)
    dates:list[date] = date_range(start=start, end=end, inc=Increment.MONTH)

    ptl:list = fake.githubdata_workflow_runs(count=15, success=True, lower_date=start, upper_date=end, real_values={'name':'Path to Live'})
    others:list = fake.githubdata_workflow_runs(count=5, success=True, lower_date=start, upper_date=end)
    source:dict = fake.githubdata_repository()
    source['workflow_runs'] = ptl + others

    merged = __merger__([source])
    data = by_month(data=merged,
                    dates=dates)

    assert len(dates) == len(data.keys())
