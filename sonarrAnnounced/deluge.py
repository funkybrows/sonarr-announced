from base64 import b64encode
import stringcase
from deluge_client import DelugeRPCClient

from sonarrAnnounced.scrapers.tl import get_torrent_from_url
import logging

logger = logging.getLogger("Deluge")
logger.setLevel(logging.DEBUG)
from sonarrAnnounced import config

cfg = config.init()


class DelugeTlRpcClient(DelugeRPCClient):
    def connect_if_necessary(self):
        if not self.connected:
            try:
                self.connect()
            except Exception:
                logger.exception("Failed to connect to deluge client")

    def add_torrent_from_url(self, title, url):
        self.connect_if_necessary()
        torrent_data = get_torrent_from_url(url)
        result = self.call(
            "core.add_torrent_file",
            stringcase.snakecase(title),
            b64encode(torrent_data),
            {},
        )
        logger.debug("Deluge result: %s", result)


def get_deluge_client():
    return DelugeTlRpcClient(
        cfg["deluge.host"],
        int(cfg["deluge.port"]),
        cfg["deluge.username"],
        cfg["deluge.password"],
    )
