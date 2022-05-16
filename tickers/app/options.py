"""Tools module."""

import json

from app.conf import config
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync


def read_tickers(tickers_file: str) -> list:
    """
    Read tickers from initial.

    Args:
        tickers_file (str): name of file with tickers name.

    Returns:
        list: list of tickers names.
    """
    with open(tickers_file) as tf:
        return json.loads(tf.read())


async def get_influx():
    """Return influx api object."""
    influx = InfluxDBClientAsync(
        url=config.url, org=config.org, token=config.token,
    )
    try:
        yield influx.query_api()
    finally:
        await influx.close()
