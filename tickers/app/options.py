import json
from app.conf import config
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync


def read_tickers(tickers_file: str) -> list:
    """
    Read tickers from initial.
    """
    with open(tickers_file) as tf:
        tickers = json.loads(tf.read())
        return tickers


async def get_influx():
    influx = InfluxDBClientAsync(url=config.url, org=config.org, token=config.token)
    try:
        yield influx.query_api()
    finally:
        await influx.close()
