import os.path

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)

import logging.config

from arrnounced import utils

logging_conf_path = f"{utils.get_config_folder_path()}/logging.conf"
log_folder_path = utils.get_log_folder_path()

try:
    logging.config.fileConfig(
        logging_conf_path,
        defaults={"log_folder_path": log_folder_path},
    )
except KeyError:
    base_msg = "COULD NOT SET UP LOGGING"
    if not os.path.exists(logging_conf_path):
        print(base_msg, logging_conf_path, "does not exist")
    if not os.path.exists(log_folder_path):
        print(base_msg, log_folder_path, "does not exist")
    raise
