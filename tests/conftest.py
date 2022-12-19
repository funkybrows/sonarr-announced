import pydle
import pytest

from arrnounced import backend, config


@pytest.fixture(scope="session")
def pydle_pool():
    return pydle.ClientPool()


@pytest.fixture(scope="session")
def user_config():
    my_user_config = config.init("/config.toml")
    backend.init(my_user_config.backends)
    return my_user_config
