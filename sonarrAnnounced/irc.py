import logging
import socket
import sys

import pydle
import pydle.client

from sonarrAnnounced import config
from sonarrAnnounced import deluge
from sonarrAnnounced import sonarr

logger = logging.getLogger(__name__)
# logger = logging.getLogger("IRC")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

cfg = config.init()


# XXX: Make global fn
sonarr_client = sonarr.get_sonarr_client()
deluge_client = deluge.get_deluge_client()


class IRCClient(
    pydle.featurize(*pydle.features.LITE),
    pydle.client.BasicClient,
):
    tracking = None
    RECONNECT_MAX_ATTEMPTS = 100
    logger = logger

    # temp fix until pydle handles connect failures
    async def connect(self, *args, **kwargs):
        logger.debug("STARTING CONNECT")
        try:
            await super().connect(*args, **kwargs)
        except socket.error:
            self.on_disconnect(expected=False)

    def set_tracker(self, track):
        self.tracking = track

    async def on_connect(self):
        logger.info(
            "Connected to: %s, joining %s",
            self.tracking["irc_host"],
            self.tracking["irc_channel"],
        )

        nick_pass = cfg["{}.nick_pass".format(self.tracking["name"].lower())]
        if nick_pass is not None and len(nick_pass) > 1:
            await self.rawmsg("NICKSERV", "IDENTIFY", nick_pass)

    async def on_raw(self, message):
        await super().on_raw(message)
        logger.debug("MESSAGE: %s", message._raw)
        if (
            cfg["{}.nick".format(self.tracking["name"].lower())] in message._raw
            and "+r" in message._raw
        ):
            logger.debug(
                "Identified with NICKSERV - joining %s", self.tracking["irc_channel"]
            )
            await self.join(self.tracking["irc_channel"])

    async def on_message(self, source, target, message):
        if source[0] != "#":
            logger.debug("%s sent us a message: %s", target, message)
        else:
            logger.debug("Message: %s, type: %s", [message], type(message))
            parsed_title, url = sonarr_client.get_parsed_tl_announcement(message)
            if parsed_title:
                push_release_response = sonarr_client.push_torrent_release(
                    parsed_title, url
                )
                if (
                    push_release_response["approved"]
                    or push_release_response["quality"]["quality"]["resolution"] == 720
                ):
                    deluge_client.add_torrent_from_url(parsed_title, url)
                else:
                    logger.debug(
                        "Title: %s with url: %s not approved, %s",
                        parsed_title,
                        url,
                        push_release_response,
                    )

    async def on_invite(self, channel, by):
        if channel == self.tracking["irc_channel"]:
            self.join(self.tracking["irc_channel"])


pool = pydle.ClientPool()
clients = []


def start(trackers):
    global cfg, pool, clients

    for tracker in trackers.loaded:
        logger.info(
            "Pooling server: %s:%d %s",
            tracker["irc_host"],
            tracker["irc_port"],
            tracker["irc_channel"],
        )

        nick = cfg["{}.nick".format(tracker["name"].lower())]
        client = IRCClient(nick)

        client.set_tracker(tracker)
        clients.append(client)
        try:
            pool.connect(
                client,
                hostname=tracker["irc_host"],
                port=tracker["irc_port"],
                tls=tracker["irc_tls"],
                tls_verify=tracker["irc_tls_verify"],
            )
        except Exception as ex:
            logger.exception("Error while connecting to: %s", tracker["irc_host"])

    try:
        pool.handle_forever()
    except Exception as ex:
        logger.exception("Exception pool.handle_forever:")


def stop():
    global pool

    for tracker in clients:
        logger.debug("Removing tracker: %s", tracker.tracking["name"])
        pool.disconnect(tracker)
