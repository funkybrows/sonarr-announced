try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)

import logging.config

from arrnounced import utils

logging.config.fileConfig(
    f"{utils.get_config_folder_path()}/logging.conf",
    defaults={"log_folder_path": utils.get_log_folder_path()},
)
