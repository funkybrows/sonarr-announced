import asyncio
import datetime as dt
import io
import json
import logging
import threading
from unittest import mock

import pytest
from aio_pika_wrapper.client import AioConnectionPool, AioClient as AioPikaClient
from tenacity import retry, stop_after_attempt, wait_fixed

from arrnounced.irc import IRC
from arrnounced.manager import _get_trackers
from arrnounced.rabbit import AioClient

LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)

LOGGER = logging.getLogger(__name__)
CLIENT_LOGGER = logging.getLogger("aio_pika_wrapper.client")
handler = logging.FileHandler("/logs/debug.log", mode="w")
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(handler)
CLIENT_LOGGER.setLevel(logging.DEBUG)
CLIENT_LOGGER.addHandler(handler)
RPC_LOGGER = logging.getLogger("arrnounced.rpc")
RPC_LOGGER.setLevel(logging.DEBUG)
RPC_LOGGER.addHandler(handler)


@pytest.mark.asyncio
@mock.patch("arrnounced.message_handler.notify")
@mock.patch("arrnounced.announcement.create_announcement")
async def test_rabbit(
    mock_notify,
    mock_announce,
    user_config,
    pydle_pool,
):
    message = "\x02\x0300,04New Torrent Announcement:\x02\x0300,12 <Movies :: BlurayRip>  Name:'Some Fake 2020 BDRip x264-Elite' uploaded by 'Anonymous' - \x0301,15 https://www.torrentleech.org/torrent/123456789"
    mock_notify.return_value = None
    in_memory_files = {"check.json": io.BytesIO()}
    access_files_lock = threading.Lock()
    expected_message_name = "Some Fake"

    @retry(reraise=True, stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def assert_w_retry():
        with access_files_lock:
            logging.debug("VALUE: %s", in_memory_files["check.json"].getvalue())
            assert (
                expected_message_name
                in json.loads(in_memory_files["check.json"].getvalue())["name"]
            )

    async def start_consuming(consumer, queue_name):
        async def callback(message):
            async with message.process():
                if message.content_type == "application/json":
                    LOGGER.debug("GOT MESSAGE: %s", json.loads(message.body))
                    try:
                        with access_files_lock:
                            in_memory_files["check.json"].write(message.body)
                    except:
                        logging.exception("ERROR")

        await consumer.start_consuming(queue_name, callback)

    async def get_announcement(message):
        tl_tracker = _get_trackers(user_config, "/autodl-trackers/trackers")["tl"]
        tl_irc = IRC(tl_tracker, pydle_pool)
        await tl_irc.on_message("#tlannounces", "_AnnounceBot_", message)
        assert mock_announce.called
        return mock_announce.call_args[0][0]

    pool = AioConnectionPool(3)
    try:

        publisher = AioClient("test-exchange", "Test_Download", pool=pool)
        await publisher.wait_until_ready(timeout=5)
        consumer = AioClient("test-exchange", "Test_Consumer", pool)
        await consumer.wait_until_ready(timeout=5)
        queue = await consumer.declare_queue(
            exclusive=True,
            durable=True,
            auto_delete=True,
        )
        await consumer.bind_queue(queue.name, routing_key="torrent.download.*.*")
        asyncio.create_task(start_consuming(consumer, queue.name))
        await publisher.publish_from_announcement(await get_announcement(message))

        await assert_w_retry()
    finally:
        await publisher.delete_exchange("test-exchange", if_unused=False)
        await pool.close()
