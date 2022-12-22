try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)

from pathlib import Path
import os
from os import path
import logging.config

from arrnounced import utils

log_file_path = path.join(
    Path(__file__).parent.parent.parent.absolute(), "config", "logging.conf"
)
print(log_file_path)
logging.config.fileConfig(
    log_file_path,
    defaults={
        "log_folder_path": os.environ.get(
            "LOG_FOLDER_PATH", utils.get_log_folder_path()
        )
    },
)
