from requests import Session
from sonarr_announced.scrapers.tl import login, get_torrent_from_url


def test_login():
    session = login()
    assert isinstance(session, Session)


def test_get_torrent_from_url():
    url = "https://www.torrentleech.org/torrent/240921196"
    response_content = get_torrent_from_url(url)
    assert isinstance(response_content, bytes)
    assert "have.you.been".encode("utf-8") in response_content
    assert "tracker.torrentleech".encode("utf-8") in response_content
