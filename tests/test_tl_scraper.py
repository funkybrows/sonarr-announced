from requests import Session
from sonarrAnnounced.scrapers.tl import login, get_torrent_from_url


def test_login():
    session = login()
    assert isinstance(session, Session)
