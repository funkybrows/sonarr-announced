import re
import requests

from sonarrAnnounced import config

cfg = config.init()


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
    torrent_info_match = re.search(r'href=("/[\S]+")>Download[\s]+Torrent', r.text)
    relative_torrent_url = re.sub(r'href="', "", torrent_info_match.group(0)).split(
        '"'
    )[0]
    r = session.get(f"{domain}{relative_torrent_url}")
    return r.content
