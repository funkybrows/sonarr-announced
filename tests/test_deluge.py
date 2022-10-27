from base64 import b64encode
from sonarrAnnounced.deluge import get_deluge_client
from sonarrAnnounced.scrapers.tl import (
    get_torrent_from_url as get_tl_torrent_from_url,
)
from sonarrAnnounced.sonarr import get_sonarr_client
from sonarrAnnounced import config
import logging
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
    deluge_client.connect_if_necessary()
    assert deluge_client.connected


# def test_get_from_url():
#     deluge_client.connect_if_necessary()
#     msg = "\x02\x0300,04New Torrent Announcement:\x02\x0300,12 <TV :: Episodes HD>  Name:'Handmade Britains Best Woodworker S02E06 1080p HDTV H264-DARKFLiX' uploaded by 'Anonymous' - \x0301,15 https://www.torrentleech.org/torrent/240921997"
#     parsed_title, url = sonarr_client.get_parsed_tl_announcement(msg)
#     deluge_client.add_torrent_from_url(parsed_title, url)
