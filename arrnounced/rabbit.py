import json
import logging
import os

from aio_pika_wrapper.client import AioClient as AioPikaClient

logger = logging.getLogger("arrnounced.rpc")

RABBIT_CLIENT = None


def get_rabbit_client(exchange_name=None, client_name=None):
    global RABBIT_CLIENT
    if not RABBIT_CLIENT:
        kwargs = {}
        if exchange_name:
            kwargs["exchange_name"] = exchange_name
        if client_name:
            kwargs["client_name"] = client_name
        RABBIT_CLIENT = AioClient(**kwargs)

    return RABBIT_CLIENT


class AioClient(AioPikaClient):
    TIMEOUT = 5

    def __init__(
        self,
        exchange_name=os.environ.get("RABBIT_EXCHANGE"),
        client_name=f"{os.environ.get('PROJECT_NAME')}-{os.environ.get('NAMESPACE')}-arrnounced-AioClient",
        pool=None,
    ):
        super().__init__(exchange=None, client_name=client_name, pool=pool)
        self.declare_exchange_name = (
            exchange_name  # not to be confused w/ AioPikaClient._exchange_name
        )

    async def connect(self):
        await super().connect()
        await self.wait_until_connected(timeout=self.TIMEOUT)
        exchange = await self.declare_exchange(
            self.declare_exchange_name,
            exchange_type="topic",
            durable=True,
            timeout=self.TIMEOUT,
        )
        if exchange:
            await self.set_exchange(self.declare_exchange_name)

    @staticmethod
    def convert_to_message(announcement):
        return {
            "name": announcement.title,
            "torrent_url": announcement.torrent_url,
            "date": announcement.date.isoformat(),
            "indexer": announcement.indexer,
        }

    async def publish_from_announcement(self, announcement, add_in_paused_state=False):
        return await self.publish_message(
            self.convert_to_message(announcement),
            add_in_paused_state=add_in_paused_state,
        )

    async def publish_message(self, message, add_in_paused_state=False):
        download_options = {}
        if add_in_paused_state:
            download_options["add_in_paused_state"] = True
        if download_options:
            message["download_options"] = download_options

        return await super().publish_message(
            f"torrent.download.url.{message['indexer'].lower()}",
            message,
            content_type="application/json",
        )
