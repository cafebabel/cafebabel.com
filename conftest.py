
def pytest_runtest_teardown():
    from cli import _initdb
    _initdb()
