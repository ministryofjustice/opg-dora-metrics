import os
import pytest
from datetime import date, datetime
from pprint import pp
from dateutil.relativedelta import relativedelta
from github.WorkflowRun import WorkflowRun
from github.Team import Team

from app.reports.github_deployment_frequency.report import reports
from fake.github.attach import attach_property

from faker import Faker
from fake.github_data.repository import FakeGithubDataRepositoryProvider
from fake.github_data.workflow_run import FakeGithubDataWorkflowRunProvider
from fake.github_data.team import FakeGithubDataTeamProvider
fake = Faker()
fake.add_provider(FakeGithubDataRepositoryProvider)
fake.add_provider(FakeGithubDataWorkflowRunProvider)
fake.add_provider(FakeGithubDataTeamProvider)


def test_reports_repository_deployments_simple():
    """Simple test to make sure report generates"""

    end:date = datetime.now() - relativedelta(days=1)
    start:date = end - relativedelta(months=2)

    parent:Team = fake.githubdata_team(real_values={'name':'OPG', 'slug':'opg'})
    # primary repo with lots of data
    # repoA:dict = fake.githubdata_repository()
    # teamsA:list[Team] = fake.githubdata_teams(count=3, real_values={'parent_id': parent['id']})
    # # workflows
    # runsA:list[WorkflowRun] = fake.githubdata_workflow_runs(count=120,
    #                                                        success=True,
    #                                                        lower_date=start,
    #                                                        upper_date=end,
    #                                                        real_values={'name':'Path to Live', 'repository_id': repoA['id']})


    # repoB:dict = fake.githubdata_repository()
    # teamsB:list[Team] = fake.githubdata_teams(count=1, real_values={'parent_id': parent['id']})
    # # workflows
    # runsB:list[WorkflowRun] = fake.githubdata_workflow_runs(count=2,
    #                                                        success=True,
    #                                                        lower_date=start,
    #                                                        upper_date=end,
    #                                                        real_values={'name':'Path to Live', 'repository_id': repoB['id']})
    # # merge for testings
    # teams = teamsA + teamsB + [parent]
    # runs = runsA + runsB

    # dur:str = '100 years'
    # data = reports(repositories=[repoA, repoB],
    #         teams=teams,
    #         deployments=runs,
    #         start=start,
    #         end=end,
    #         args={},
    #         timings={
    #             'duration': dur
    #         })

    # # now test this has all worked
    # deploys = data['raw.json']['deployments']
    # deploys_by_month = deploys['per_month']
    # deploys_by_team = deploys['per_team_per_month']
    # deploys_by_repo = deploys['per_repo_per_month']
    # ############### A's
    # # check the teams
    # counter:int = 0
    # for t in teamsA:
    #     slug = t['slug']
    #     for ym, values in deploys_by_team[slug].items():
    #         total, _ = values
    #         counter += total
    # # all A teams are added all repos A
    # assert len(runsA) * len(teamsA) == counter
    # # all runs are mapped to a yeam-month
    # counter = 0
    # for ym, values in deploys_by_repo[repoA['full_name']].items():
    #     total, _ = values
    #     counter += total
    # assert len(runsA) == counter
    # ############### B's
    # # check the teams
    # counter:int = 0
    # for t in teamsB:
    #     slug = t['slug']
    #     for ym, values in deploys_by_team[slug].items():
    #         total, _ = values
    #         counter += total
    # # all A teams are added all repos A
    # assert len(runsB) * len(teamsB) == counter
    # # all runs are mapped to a yeam-month
    # counter = 0
    # for ym, values in deploys_by_repo[repoB['full_name']].items():
    #     total, _ = values
    #     counter += total
    # assert len(runsB) == counter

    # ##### overall
    # counter = 0
    # for ym, values in deploys_by_month.items():
    #     total, _ = values
    #     counter += total
    # assert len(runsA) + len(runsB) == counter

    # # check duration is in there
    # checkfor:str = f'in {dur}'
    # assert True == (checkfor in data['by_month/index.html.md.erb'])
