import asyncio
import re
from unittest import mock

import pytest

from arrnounced.manager import _get_trackers
from arrnounced.irc import IRC


@mock.patch("arrnounced.message_handler.get_rabbit_client")
@mock.patch("arrnounced.message_handler.notify")
@mock.patch("arrnounced.announcement.create_announcement")
@pytest.mark.asyncio
async def test_announcement_generated(
    mock_notify,
    mock_announce,
    mock_get_rabbit,
    pydle_pool,
    user_config,
    tracker_folder_path,
):
    mock_get_rabbit.return_value = (rabbit_mock := mock.AsyncMock())
    rabbit_mock.wait_until_ready.return_value = asyncio.Future()

    message = "\x02\x0300,04New Torrent Announcement:\x02\x0300,12 <Movies :: BlurayRip>  Name:'Eat Wheaties 2020 BDRip x264-JustWatch' uploaded by 'Anonymous' - \x0301,15 https://www.torrentleech.org/torrent/123456789"
    tl_tracker = _get_trackers(user_config, f"{tracker_folder_path}/trackers")["tl"]
    tl_irc = IRC(tl_tracker, pydle_pool)
    mock_notify.return_value = None
    await tl_irc.on_message("#tlannounces", "_AnnounceBot_", message)
    announcement = mock_announce.call_args[0][0]
    assert re.search(
        rf"http[s]?://{tl_tracker.config._xml_config.tracker_info['siteName']}/rss/download/\d+/[a-z0-9]+/Eat\+Wheaties\+2020\+BDRip\+x264-JustWatch",
        announcement.torrent_url,
    )
