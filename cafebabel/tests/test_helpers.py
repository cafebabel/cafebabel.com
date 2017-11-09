from ..core.helpers import reading_time


def test_reading_time_returns_duration_in_minutes():
    assert reading_time('word') == 1
    assert reading_time(' word' * 600) == 3
    assert reading_time(' word' * 6000) == 24
