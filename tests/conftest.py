import pydle
import pytest

from arrnounced import backend, config, utils


@pytest.fixture(scope="session")
def pydle_pool():
    return pydle.ClientPool()


@pytest.fixture(scope="session")
def config_file_path():
    return f"{utils.get_config_folder_path()}/config.toml"


@pytest.fixture(scope="session")
def tracker_folder_path():
    return utils.get_tracker_folder_path()


@pytest.fixture(scope="session")
def user_config(config_file_path):
    my_user_config = config.init(config_file_path)
    backend.init(my_user_config.backends)
    return my_user_config
