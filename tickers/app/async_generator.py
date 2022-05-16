"""
Async generator module.

Contains AsyncInfluxAPI and GeneratorManager classes.
"""

import asyncio
import logging
import random

from app.conf import config
from influxdb_client import Point
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

logging.basicConfig(level=logging.INFO)


class AsyncInfluxAPI(object):
    """Async influx api class."""

    def __init__(self, client: InfluxDBClientAsync):
        """
        Initialize of influx api class.

        Args:
            client (InfluxDBClientAsync): instance of influx client.
        """
        self.client: InfluxDBClientAsync = client
        self.write_api = self.client.write_api()
        self.read_api = self.client.query_api()
        self.org = config.org

    @classmethod
    def generate_movement(cls) -> int:
        """
        Increment movement. Movement depends on random value.

        Returns:
            int: The movement value.
        """
        crypto = random.SystemRandom()
        return -1 if crypto.random() < 0.5 else 1

    async def get_price(self, query_string: str) -> int:
        """
        Get new price for ticker.

        Args:
            query_string (str): text of query.

        Returns:
            int: ticker price with movement.
        """
        prices = await self.read_api.query(query=query_string, org=self.org)
        if not prices:
            return 0
        price = prices[0].records[0].get_value()
        return price + self.generate_movement()

    async def write_price(
            self, bucket: str, ticker: str, price_value: int,
    ) -> None:
        """
        Write price to influx.

        Args:
            bucket (str): bucket in influxdb.
            ticker (str): name of ticker.
            price_value (int): ticker's price.
        """
        point = Point(ticker).field('price', price_value)
        await self.write_api.write(bucket=bucket, org=self.org, record=point)


class GeneratorManager(object):
    """Class for generation."""

    @classmethod
    async def process_ticker(
            cls, api: AsyncInfluxAPI, ticker: str, timeout: int = 1,
    ) -> None:
        """
        Process single ticker.

        Args:
            api (AsyncInfluxAPI): api.
            ticker (str): name of ticker.
            timeout (int): value of timeout.
        """
        while True:
            query_string = f'from(bucket:"tickers")\
            |> range(start: -7d)\
            |> filter(fn: (r) => r["_measurement"] == "{ticker}")\
            |> filter(fn: (r) => r["_field"] == "price")\
            |> last()'  # noqa:  N400
            new_price = await api.get_price(query_string)
            await api.write_price(
                bucket=config.bucket, ticker=ticker, value=new_price,
            )
            logging.info(f'Send {new_price} to {ticker}')
            await asyncio.sleep(timeout)

    @classmethod
    async def run(cls, tickers: list) -> None:
        """
        Start processing.

        Args:
            tickers (list): list of tickers.
        """
        async with InfluxDBClientAsync(
                url=config.url,
                org=config.org,
                token=config.token,
                verify_ssl=False,
        ) as client:
            api = AsyncInfluxAPI(client)
            tasks = []
            for ticker in tickers:
                tasks.append(
                    asyncio.create_task(cls.process_ticker(api, ticker)),
                )

            await asyncio.gather(*tasks)
