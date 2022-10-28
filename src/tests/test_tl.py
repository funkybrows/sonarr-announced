import asyncio
import logging
import sys
from pathlib import Path
from threading import Thread
from time import time


import nest_asyncio
import pytest
from sonarr_announced.trackers import Trackers
from sonarr_announced.irc import IRCClient, cfg
from test import get_tl_client

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


Path("./tests/testOutput").mkdir(parents=True, exist_ok=True)


def get_tl():
    return Trackers().get_tracker("torrentleech")


@pytest.mark.asyncio
async def test_asyncio():
    start = time()

    async def do_this():
        logger.debug("Do this at %s", time() - start)
        task_1 = asyncio.create_task(asyncio.sleep(2))
        task_2 = asyncio.create_task(do_that())
        await task_1
        await task_2

    async def do_that():
        logger.debug("Do that at %s", time() - start)
        await asyncio.sleep(2)

    async def do_these():
        logger.debug("Do these at %s", time() - start)
        await asyncio.sleep(2)

    tasks = []
    for _ in range(3):
        tasks.append(asyncio.create_task(do_this()))
        tasks.append(asyncio.create_task(do_these()))
    for task in tasks:
        await task


@pytest.mark.asyncio
async def test_tracker_connects():
    file_path = "./tests/testOutput/connects.txt"
    with open(file_path, "w") as f:
        pass

    class TestIRCClient(IRCClient):
        async def connect(self, hostname=None, port=None, reconnect=False, **kwargs):
            if (not hostname or not port) and not reconnect:
                logger.error("Have to specify hostname and port if not reconnecting.")
                raise ValueError(
                    "Have to specify hostname and port if not reconnecting."
                )

            # Reset attributes and connect.
            if not reconnect:
                self._reset_connection_attributes()
            await self._connect(
                hostname=hostname, port=port, reconnect=reconnect, **kwargs
            )

            await self.handle_forever()

        async def handle_forever(self):
            data = await self.connection.recv(timeout=self.READ_TIMEOUT)
            with open(file_path, "a") as f:
                f.write(data.decode("utf-8"))

    client = TestIRCClient(cfg["torrentleech.nick"])
    client.set_tracker(get_tl_client())
    tl = Trackers().get_tracker("torrentleech")

    await client.connect(
        hostname=tl["irc_host"], port=tl["irc_port"], tls=tl["irc_tls"]
    )
    with open(file_path) as f:
        assert "Registration Timeout" in f.read()


@pytest.mark.asyncio
async def test_stop_runforever(event_loop):
    from threading import Thread

    nest_asyncio.apply(event_loop)
    new_loop = asyncio.new_event_loop()

    async def do_something_forever_until():
        counter = 1
        while counter < 5:
            await asyncio.sleep(1)
            counter += 1
        thread = Thread(target=new_loop.call_soon_threadsafe(new_loop.stop))
        thread.start()

    new_loop.create_task(do_something_forever_until())
    new_loop.run_forever()


@pytest.mark.asyncio
async def test_tracker_registration():

    file_path = "./tests/testOutput/connects.txt"
    with open(file_path, "w") as f:
        pass

    class TestIRCClient(IRCClient):
        async def connect(self, *args, **kwargs):
            await super().connect(*args, **kwargs)
            await self.on_connect()
            with open(file_path, "a") as f:
                f.write("JOINED")

    client = TestIRCClient(cfg["torrentleech.nick"])
    client.set_tracker(Trackers().get_tracker("torrentleech"))
    tl = Trackers().get_tracker("torrentleech")
    # XXX: We're cutting off self.handle_forever, which will trigger a warning
    await (
        client.connect(hostname=tl["irc_host"], port=tl["irc_port"], tls=tl["irc_tls"])
    )
    with open(file_path) as f:
        assert "JOINED" in f.read()
