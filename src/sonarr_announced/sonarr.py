import datetime as dt
import logging

import re
import requests
from pyarr import SonarrAPI

from sonarr_announced import utils
from sonarr_announced import config

logger = logging.getLogger("SONARR")
logger.setLevel(logging.DEBUG)
cfg = config.init()


class SonarrClient(SonarrAPI):
    def get_parsed_title_from_sonarr(self, name):
        return self.get_parsed_title(name)["title"]

    def push_torrent_release(self, parsed_title, url):
        return self.push_release(
            parsed_title,
            url,
            "Torrent",
            (dt.datetime.utcnow() - dt.timedelta(minutes=10)).isoformat(),
        )


def get_sonarr_client():

    api_key = cfg["sonarr.apikey"]
    url = cfg["sonarr.url"]

    return SonarrClient(url, api_key)


def wanted(title, download_link, indexer):
    global cfg
    approved = False

    logger.debug(
        "Notifying Sonarr of release from %s: %s @ %s", indexer, title, download_link
    )

    headers = {"X-Api-Key": cfg["sonarr.apikey"]}
    params = {
        "title": utils.replace_spaces(title, "."),
        "downloadUrl": download_link,
        "protocol": "Torrent",
        "publishDate": dt.datetime.now().isoformat(),
        "indexer": indexer,
    }

    resp = requests.post(
        url="{}/api/release/push".format(cfg["sonarr.url"]),
        headers=headers,
        params=params,
    ).json()
    if "approved" in resp:
        approved = resp["approved"]

    return approved
