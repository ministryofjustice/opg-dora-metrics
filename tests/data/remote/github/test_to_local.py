import os
import pytest
from datetime import date
from pprint import pp

from github import Github
from github.Repository import Repository
from app.data.local.github_data.map import Local
from app.data.remote.github.to_local import to_local


@pytest.mark.skipif(os.environ.get('GITHUB_TEST_TOKEN', 0) == 0, reason='Requires github token to run')
def test_data_remote_github_repository_to_local_using_real_repository():
    """Test the a real repository"""
    
    g:Github = Github(os.environ.get('GITHUB_TEST_TOKEN'))
    data = to_local(g=g, 
                    reopsitory_slug="ministryofjustice/serve-opg",
                    start=date(year=2024, month=4, day=1),
                    end=date(year=2024, month=4, day=30),
                    get_artifacts=True,
                    )
    # test against real world known values
    assert 23 == len(data.get('workflow_runs'))
    assert 23 == len(data.get('artifacts'))
    assert False == data['archived']
    assert 'main' == data['default_branch']
    pp(data)
    