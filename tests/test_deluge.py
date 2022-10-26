from base64 import b64encode
from sonarrAnnounced.deluge import get_deluge_client
from sonarrAnnounced.scrapers.tl import (
    get_torrent_from_url as get_tl_torrent_from_url,
    get_torrent_url_from_url as get_tl_torrent_url_from_url,
)
from sonarrAnnounced.sonarr import get_sonarr_client
from sonarrAnnounced import config
import logging
import requests
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

sonarr_client = get_sonarr_client()
deluge_client = get_deluge_client()
cfg = config.init()


def test_connect():
    deluge_client.connect()
    assert deluge_client.connected
