import os
import pytest
from pprint import pp

from app.data.local.github_data.map import RepositoryBaselineComplianceAttributes
from app.data.local.standards.repository_standards_compliance import repository_standards
from app.reports.github_repository_standards.report import single_report, overview_report
from faker import Faker
from fake.github_data.repository import FakeGithubDataRepositoryProvider
fake = Faker()
fake.add_provider(FakeGithubDataRepositoryProvider)


# def test_reports_repository_standards_compliance_report_single():
#     """Simple test to make sure report generates and has a flag to true for expected result"""

#     source:dict = fake.githubdata_repository()
#     for k in RepositoryBaselineComplianceAttributes.keys():
#         source[k] = True
#     source['standards'] = repository_standards(source)
#     report:str = single_report(source).strip()

#     checkfor:str = "Default branch is called main</td><td style='text-align:right;'>True</td>"

#     assert True == (checkfor in report)


# def test_reports_repository_standards_compliance_report_overview():
#     """Simple test to make sure report generates and has a flag to true for expected result"""

#     source:dict = fake.githubdata_repository()
#     for k in RepositoryBaselineComplianceAttributes.keys():
#         source[k] = True
#     source['standards'] = repository_standards(source)
#     report:str = overview_report([source], '1 year 10 months')

#     checkpassed:str = "- **Passed baseline checks**: 1 / 1"
#     checkdur:str = "in 1 year 10 months*"

#     assert True == (checkpassed in report)
#     assert True == (checkdur in report)
