from asyncio import futures
from asyncore import write
from time import time
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import random
import time
import concurrent
import logging
from conf import config
from options import read_tickers

logging.basicConfig(level=logging.INFO)


class TickersGenerator:
    def __init__(self, num_executors: int = 100) -> None:
        self.read_client = influxdb_client.InfluxDBClient(url=config.url, token=config.token, org=config.org)
        self.write_client = influxdb_client.InfluxDBClient(url=config.url, token=config.token, org=config.org)        
        self.num_executors = num_executors


    def generate_movement(self) -> int:
        """
        Increment movement.
        
        Movement depends on random value.
        Returns:
            The movement value.
        """
        movement = -1 if random.random() < 0.5 else 1
        return movement

    def write(self, influx_client: influxdb_client.InfluxDBClient, ticker: str, value: int) -> None:
        """
        Write data to influx

        Args:
            influx_client (InfluxDBClient): object of influx client.
            ticker (str): name of ticker.
            value (int): value of tickers.
        Returns:
            Value of 
        """
        write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        point = influxdb_client.Point(ticker).field("price", value)
        write_api.write(bucket="tickers", org="skanestas", record=point)

    def get_price(self, influx_client: influxdb_client.InfluxDBClient, ticker: str) -> int:
        """
        Increment calculation.

        Make request to Influx for last value of ticker and make add movement to it.
        Args:
            influx_client (InfluxDBClient): object of influx client.
            ticker (str): ticker name.

        Returns:
            Value of price for next step.
        """
        query_api = influx_client.query_api()
        query_string = f' from(bucket:"tickers")\
        |> range(start: -50m)\
        |> filter(fn: (r) => r["_measurement"] == "{ticker}")\
        |> filter(fn: (r) => r["_field"] == "price")\
        |> last()'
        result = query_api.query(query=query_string, org="skanestas")
        if not result:
            return 0
        price = result[0].records[0].get_value()
        return price + self.generate_movement()

    def produce(self, ticker: str, timeout: int = 1) -> None:
        """
        Calculates the ticker price send it to influx

        Args:
            ticker (str): ticker name.
            timeout (int): timeout sec
        """

        while True:
            price = self.get_price(self.write_client, ticker)
            self.write(self.write_client, ticker, price)
            logging.info(f"Send {price} to {ticker}")
            time.sleep(timeout)

    def run(self, tickers: list) -> None:
        """
        Main function to run.

        Args:
            tickers (list): list of tickers names
        """
        with concurrent.futures.ThreadPoolExecutor(self.num_executors) as executor:
            futures = []
            for ticker in tickers:
                futures.append(executor.submit(self.produce, ticker=ticker))
            for _ in concurrent.futures.as_completed(futures):
                pass

if __name__ == '__main__':
    tickers = read_tickers("tickers.json")
    TickersGenerator().run(tickers)
