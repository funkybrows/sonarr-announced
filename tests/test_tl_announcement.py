import re
from unittest import mock

import pytest
from arrnounced.manager import _get_trackers
from arrnounced.irc import IRC


@mock.patch("arrnounced.message_handler.notify")
@mock.patch("arrnounced.announcement.create_announcement")
@pytest.mark.asyncio
async def test_announcement_generated(
    mock_notify, mock_announce, pydle_pool, user_config
):
    message = "\x02\x0300,04New Torrent Announcement:\x02\x0300,12 <Movies :: BlurayRip>  Name:'Eat Wheaties 2020 BDRip x264-JustWatch' uploaded by 'Anonymous' - \x0301,15 https://www.torrentleech.org/torrent/240943437"
    tl_tracker = _get_trackers(user_config, "/autodl-trackers/trackers")["tl"]
    tl_irc = IRC(tl_tracker, pydle_pool)
    mock_notify.return_value = None
    await tl_irc.on_message("#tlannounces", "_AnnounceBot_", message)
    announcement, backends = (
        mock_announce.call_args[0][0],
        mock_announce.call_args[0][1],
    )
    assert re.search(
        rf"http[s]?://{tl_tracker.config._xml_config.tracker_info['siteName']}/rss/download/\d+/[a-z0-9]+/Eat\+Wheaties\+2020\+BDRip\+x264-JustWatch",
        announcement.torrent_url,
    )
