import pydle
import pytest


@pytest.fixture(scope="session")
def pydle_pool():
    return pydle.ClientPool()
