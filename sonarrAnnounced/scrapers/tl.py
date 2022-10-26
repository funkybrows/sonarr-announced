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
