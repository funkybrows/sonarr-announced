import asyncio
import logging
import sys
from pathlib import Path


import pytest
from sonarrAnnounced.trackers import Trackers
from sonarrAnnounced.irc import IRCClient, cfg
from test import get_tl_client

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def make_dir():
    Path("./tests/testOutput").mkdir(parents=True, exist_ok=True)


def get_tl():
    return Trackers().get_tracker("torrentleech")


@pytest.mark.asyncio
async def test_tracker_connects():
    with open("./tests/testOutput/connects.txt", "w") as f:
        pass

    class TestIRCClient(IRCClient):
        async def on_data(self, data):
            try:
                with open("./tests/testOutput/connects.txt", "a") as f:
                    f.write("CONNECTED2")
                    f.write(data)
            except Exception:
                # logger.exception("Didn't work")
                pass

        async def handle_forever(self):
            if self.connected:
                with open("./tests/testOutput/connects.txt", "a") as f:
                    f.write("CONNECTED")
                try:
                    data = await self.connection.recv(timeout=self.READ_TIMEOUT)
                except asyncio.TimeoutError:
                    pass
                with open("./tests/testOutput/connects.txt", "a") as f:
                    f.write("HERE")
                if not data:
                    # logger.error("No data recieved")
                    raise Exception("No data recieved")

            else:
                raise Exception("No connection")
            await self.on_data(data)

    async def do_sleep():
        await asyncio.sleep(4)

    async def is_connected():
        counter = 0
        while counter < 5:
            with open("testOutput/connects.txt") as f:
                if "CONNECTED" in f.read():
                    return True
            counter += 1
            await asyncio.sleep(1)
        return False

    client = TestIRCClient(cfg["torrentleech.nick"])
    client.set_tracker(get_tl_client())
    tl = Trackers().get_tracker("torrentleech")

    task_1 = asyncio.create_task(
        client.connect(hostname=tl["irc_host"], port=tl["irc_port"], tls=tl["irc_tls"])
    )
    # task_2 = asyncio.create_task(do_sleep())
    await task_1
    stop
    # result = await task_2
    # assert result


# client = IRCClient("cap_with_both_knees")
# client.set_tracker(tl)
# client.run(
#     hostname=tl["irc_host"],
#     port=tl["irc_port"],
#     tls=tl["irc_tls"],
# )
