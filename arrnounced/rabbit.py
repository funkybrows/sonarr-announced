import json
import logging
import os

from aio_pika_wrapper.client import AioClient as AioPikaClient

logger = logging.getLogger("arrnounced.rpc")


class AioClient(AioPikaClient):
    TIMEOUT = 5

    def __init__(
        self,
        exchange_name=os.environ.get("RABBIT_EXCHANGE"),
        client_name=None,
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
