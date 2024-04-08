import pytest
from datetime import date
from metrics.github import deployment_frequency
from pprint import pp

from github import Github

def test_metrics_github():
    """"""

    # deployment_frequency(
    #     repositories= [
    #         {'repo':"ministryofjustice/opg-github-actions", 'branch':"main", 'workflow': ' live'},
    #         {'repo':"ministryofjustice/serve-opg", 'branch':"main", 'workflow': ' live'}
    #     ],
    #     start=date(year=2024, month=2, day=1),
    #     end=date(year=2024, month=3, day=20),
    #     g=Github(),
    # )
