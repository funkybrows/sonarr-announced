import logging
import sys

print(sys.path)
from pluginbase import PluginBase

from sonarrAnnounced.config import cfg
from sonarrAnnounced import utils


logger = logging.getLogger("TRACKERS")
logger.setLevel(logging.DEBUG)


class Trackers(object):
    plugin_base = None
    source = None
    loaded = []

    def __init__(self):
        self.plugin_base = PluginBase(package="trackers")
        self.source = self.plugin_base.make_plugin_source(
            searchpath=[f"{cfg['project_root']}/sonarrAnnounced/trackers"],
            identifier="trackers",
        )

        # Load all trackers
        logger.info("Loading trackers...")
        logger.debug("PLUGINS %s", self.source.list_plugins())
        for tmp in self.source.list_plugins():
            tracker = self.source.load_plugin(tmp)
            loaded = tracker.init()
            if loaded:
                logger.info("Initialized tracker: %s", tracker.name)

                self.loaded.append(
                    {
                        "name": tracker.name.lower(),
                        "irc_host": tracker.irc_host,
                        "irc_port": tracker.irc_port,
                        "irc_channel": tracker.irc_channel,
                        "irc_tls": tracker.irc_tls,
                        "irc_tls_verify": tracker.irc_tls_verify,
                        "plugin": tracker,
                    }
                )
            else:
                logger.info("Problem initializing tracker: %s", tracker.name)

    def get_tracker(self, name):
        if len(self.loaded) < 1:
            logger.debug("No trackers loaded...")
            return None

        tracker = utils.find_tracker(self.loaded, "name", name.lower())
        if tracker is not None:
            return tracker

        return None
