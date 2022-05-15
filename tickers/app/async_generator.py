import asyncio

from app.conf import config
import logging
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client import Point
import random


logging.basicConfig(level=logging.INFO)


class AsyncInfluxAPI:
    def __init__(self, client: InfluxDBClientAsync):
        self.client: InfluxDBClientAsync = client
        self.write_api = self.client.write_api()
        self.read_api = self.client.query_api()
        self.org = config.org

    @classmethod
    def generate_movement(cls) -> int:
        """
        Increment movement.

        Movement depends on random value.
        Returns:
            The movement value.
        """
        movement = -1 if random.random() < 0.5 else 1
        return movement

    async def get_price(self, query_string: str) -> int:
        logging.info("123456789")
        result = await self.read_api.query(query=query_string, org=self.org)
        logging.info(result)
        if not result:
            return 0
        price = result[0].records[0].get_value()
        return price + self.generate_movement()

    async def write_price(self, bucket: str, ticker: str, value: int) -> None:
        point = Point(ticker).field("price", value)
        await self.write_api.write(bucket=bucket, org=self.org, record=point)


class GeneratorManager:
    @classmethod
    async def process_ticker(cls, api: AsyncInfluxAPI, ticker: str, timeout: int = 1) -> None:
        while True:
            query_string = f'from(bucket:"tickers")\
            |> range(start: -7d)\
            |> filter(fn: (r) => r["_measurement"] == "{ticker}")\
            |> filter(fn: (r) => r["_field"] == "price")\
            |> last()'
            new_price = await api.get_price(query_string)
            await api.write_price(bucket=config.bucket, ticker=ticker, value=new_price)
            logging.info(f"Send {new_price} to {ticker}")
            await asyncio.sleep(timeout)

    @classmethod
    async def run(cls, tickers: list) -> None:
        async with InfluxDBClientAsync(url=config.url, org=config.org, token=config.token, verify_ssl=False) as client:
            api = AsyncInfluxAPI(client)
            tasks = []
            for ticker in tickers:
                tasks.append(asyncio.create_task(cls.process_ticker(api, ticker)))

            await asyncio.gather(*tasks)

