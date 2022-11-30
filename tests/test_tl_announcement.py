import re
import pytest
from arrnounced import config
from arrnounced.announcement import Announcement
from arrnounced.manager import _get_trackers
from arrnounced.irc import IRC


@pytest.mark.asyncio
async def test_announcement_generated(pydle_pool):
    message = "\x02\x0300,04New Torrent Announcement:\x02\x0300,12 <Movies :: BlurayRip>  Name:'Eat Wheaties 2020 BDRip x264-JustWatch' uploaded by 'Anonymous' - \x0301,15 https://www.torrentleech.org/torrent/240943437"
    tl_tracker = _get_trackers(
        config.init("/config.toml"), "/autodl-trackers/trackers"
    )["tl"]
    tl_irc = IRC(tl_tracker, pydle_pool)
    announcement = await tl_irc.on_message("#tlannounces", "_AnnounceBot_", message)
    assert re.search(
        rf"http[s]?://{tl_tracker.config._xml_config.tracker_info['siteName']}/rss/download/\d+/[a-z0-9]+/Eat\+Wheaties\+2020\+BDRip\+x264-JustWatch",
        announcement.torrent_url,
    )
