import pytest
from timer.stopwatch import start, stop, duration, durations



@pytest.mark.parametrize("test_start, test_stop, expected",
[
    # same time
    ("2024-03-26T08:47:21.029473+00:00", "2024-03-26T08:47:21.029473+00:00", 0),
    # 20.7 seconds, so should get a rounded version to 21
    ("2024-03-26T08:47:21.029473+00:00", "2024-03-26T08:47:41.794944+00:00", 21),
    # exactly 20 seconds
    ("2024-03-26T08:40:21.000000+00:00", "2024-03-26T08:40:41.000000+00:00", 20),
    # 1 hour
    ("2024-03-26T07:40:21.000000+00:00", "2024-03-26T08:40:21.000000+00:00", 3600),
    # 1 day in seconds
    ("2024-03-25T08:40:21.000000+00:00", "2024-03-26T08:40:21.000000+00:00", 86400),
])
def test_duration_success(test_start: str, test_stop: str, expected: int):
    assert duration(test_start, test_stop) == expected



@pytest.mark.parametrize("test_start, test_stop, expected", [
    ("2024-03-26T08:47:21.029473+00:00", "2024-03-26T08:47:41.794944+00:00", 20.765471)
])
def test_durations(test_start: str, test_stop: str, expected: float):
    dur = durations(test_start, test_stop)
    assert dur['seconds'] == expected
