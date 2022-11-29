import logging
import re
import requests
import sys

from sonarr_announced import config
from sonarr_announced.trackers.tl import get_dl_link

cfg = config.init()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def login():
    session = requests.Session()
    payload = {
        "username": cfg["torrentleech.torrent_username"],
        "password": cfg["torrentleech.torrent_pass"],
    }

    r = session.post("https://www.torrentleech.org/user/account/login/", data=payload)
    assert re.search(
        r'class="user_[\w]+">' + cfg["torrentleech.torrent_username"], r.text
    )
    return session


def get_torrent_data(name, torrent_id):
    session = login()
    r = session.get(link := get_dl_link(name, torrent_id))
    logger.debug("URL: %s", link)
    return r.content
