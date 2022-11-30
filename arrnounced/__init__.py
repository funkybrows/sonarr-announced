try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)

from pathlib import Path
from os import path
import logging.config

log_file_path = path.join(
    Path(__file__).parent.parent.absolute(), "src", "config", "logging.conf"
)
logging.config.fileConfig(log_file_path)
