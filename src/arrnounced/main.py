import os
import os.path
import sys

from pathlib import Path

from arrnounced import backend, config, irc, utils
from manager import _get_trackers, get_tracker_xml_configs

import pika

if __name__ == "__main__":
    trackers_path = f"{utils.get_tracker_folder_path()}/trackers"
    p = Path(trackers_path)

    config_folder_path = utils.get_config_folder_path()

    user_config = config.init(f"{config_folder_path}/config.toml")
    backend.init(user_config.backends)
    trackers = _get_trackers(user_config, trackers_path)
    irc.run(trackers)
