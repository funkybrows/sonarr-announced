import re
from unittest import mock

import pytest
from arrnounced.manager import _get_trackers
from arrnounced.irc import IRC


@pytest.mark.asyncio
async def test_release(pydle_pool, user_config):
    message = "\x02\x0300,04New Torrent Announcement:\x02\x0300,12 <TV :: Episodes HD>  Name:'My Fake Torrent S02E07 1080p x265-Elite' uploaded by 'Anonymous' - \x0301,15 https://www.torrentleech.org/torrent/123456789"
    tl_tracker = _get_trackers(user_config, "/autodl-trackers/trackers")["tl"]
    tl_irc = IRC(tl_tracker, pydle_pool)
    with mock.patch("arrnounced.message_handler.notify") as mock_notify:
        await tl_irc.on_message("#tlannounces", "_AnnounceBot_", message)
        announcement, backends = (
            mock_notify.call_args[0][0],
            mock_notify.call_args[0][1],
        )
    json_response = await backends[0]._send_notification(announcement)
    assert json_response[0]["rejected"]
    assert "Unknown Series" in json_response[0]["rejections"]
