import logging
import sys

from sonarrAnnounced.trackers import Trackers
from sonarrAnnounced.irc import IRCClient, cfg


tl = Trackers().get_tracker("torrentleech")


def get_tl_client():
    client = IRCClient(cfg["torrentleech.nick"])
    client.set_tracker(tl)
    return client


if __name__ == "__main__":
    client = get_tl_client()
    client.run(
        hostname=tl["irc_host"],
        port=tl["irc_port"],
        tls=tl["irc_tls"],
    )
