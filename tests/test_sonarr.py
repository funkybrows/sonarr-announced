import asyncio
import datetime as dt
import nest_asyncio
import pytest
from sonarrAnnounced.sonarr import get_sonarr_client

client = get_sonarr_client()


def test_connect():
    assert client.get_series(1)["id"] == 1


def test_parse():
    msg = "\x02\x0300,04New Torrent Announcement:\x02\x0300,12 <TV :: Episodes HD>  Name:'Tell Me Lies S01E10 720p WEB H264-GLHF' uploaded by 'Anonymous' - \x0301,15 https://www.torrentleech.org/torrent/240921295"
    parsed_title, url = client.get_parsed_tl_announcement(msg)
    assert parsed_title == "Tell Me Lies S01E10 720p WEB H264-GLHF"
    assert url == "https://www.torrentleech.org/torrent/240921295"


