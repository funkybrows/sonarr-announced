import asyncio
import datetime as dt
import nest_asyncio
import pytest
from sonarrAnnounced.sonarr import get_sonarr_client

client = get_sonarr_client()


def test_connect():
    assert client.get_series(1)["id"] == 1
