"""Module with configurations for backend service."""


class Config(object):
    """Config class."""

    bucket: str = 'tickers'
    org: str = 'skanestas'
    token: str = 'token-test'
    url: str = 'http://influxdb:8086'
    service_name: str = 'tickers_generator'


config = Config()
