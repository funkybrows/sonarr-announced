import sys

from pathlib import Path

from arrnounced import config, irc, backend
from manager import _get_trackers, get_tracker_xml_configs

import pika

if __name__ == "__main__":
    trackers_path = "/autodl-trackers/trackers"
    p = Path(trackers_path)

    conf_path = "/config.toml"

    user_config = config.init(conf_path)
    backend.init(user_config.backends)
    trackers = _get_trackers(user_config, trackers_path)
    irc.run(trackers)
