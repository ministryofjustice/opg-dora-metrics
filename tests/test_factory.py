import pytest
from datetime import datetime, timezone
from tests.factory import faux
from pprint import pp


def test_factory_set_known_attribute():
    """Generate a fake pull request, test that the set value matches exactly"""
    # checl
    d = datetime.now()
    pr = faux.PullRequest(merged_at=d.isoformat())
    assert pr.merged_at == d


def test_factory_date_in_range():
    """Test date created is within range"""
    start = datetime(2024, 1, 1, 0, 0, 0)
    end = datetime(2024, 3, 1, 0, 0, 0)
    pr = faux.PullRequest(start=start, end=end)
    assert pr.merged_at >= start and pr.merged_at <= end

def test_factory_type_match():

    pr = faux.PullRequest()
    assert type(pr.number) == int
    # PullRequest requires a str inbound, but outputs as a datetime
    assert type(pr.merged_at) == datetime
    assert type(pr.title) == str
    assert type(pr.state) == str
