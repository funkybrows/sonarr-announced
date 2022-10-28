import logging
import re
import requests
import sys

from sonarr_announced import config

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


def get_torrent_from_url(url):
    domain = re.search(r"http[s]?://www.torrentleech.[\w]+", url).group(0)
    session = login()
    r = session.get(url)
    logger.debug("URL: %s", url)
    torrent_info_match = re.search(r'href=("/[\S]+")>Download[\s]+Torrent', r.text)
    relative_torrent_url = re.sub(r'href="', "", torrent_info_match.group(0)).split(
        '"'
    )[0]
    r = session.get(f"{domain}{relative_torrent_url}")
    return r.content
