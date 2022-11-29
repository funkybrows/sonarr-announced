import sys

from sonarr_announced.trackers.tl import get_name_url_from_msg

print(sys.path)
import asyncio
import datetime as dt
import nest_asyncio
import pytest
from sonarr_announced.sonarr import get_sonarr_client

client = get_sonarr_client()


def test_connect():
    assert client.get_series(1)["id"] == 1


def test_parse():
    msg = "\x02\x0300,04New Torrent Announcement:\x02\x0300,12 <TV :: Episodes HD>  Name:'Tell Me Lies S01E10 720p WEB H264-GLHF' uploaded by 'Anonymous' - \x0301,15 https://www.torrentleech.org/torrent/240921295"
    name, _ = get_name_url_from_msg(msg)
    parsed_title = client.get_parsed_title_from_sonarr(name)
    assert parsed_title == "Tell Me Lies S01E10 720p WEB H264-GLHF"


def test_push_torrent_release():
    msg = "\x02\x0300,04New Torrent Announcement:\x02\x0300,12 <TV :: Episodes HD>  Name:'Tell Me Lies S01E10 720p WEB H264-GLHF' uploaded by 'Anonymous' - \x0301,15 https://www.torrentleech.org/torrent/240921295"
    name, url = get_name_url_from_msg(msg)
    parsed_title = client.get_parsed_title_from_sonarr(name)
    push_release_info = client.push_torrent_release(parsed_title, url)
    assert push_release_info["rejected"] == True


def test_no_elements():
    msg = "\x02\x0300,04New Torrent Announcement:\x02\x0300,12 <Games :: Nintendo Switch>  Name:'Cubic Figures Update v1 1 0 NSW-SUXXORS' uploaded by 'Anonymous' - \x0301,15 https://www.torrentleech.org/torrent/240922005"
    name, url = get_name_url_from_msg(msg)
    parsed_title = client.get_parsed_title_from_sonarr(name)
    push_release_info = client.push_torrent_release(parsed_title, url)
    print(push_release_info)
    stop
