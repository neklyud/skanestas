"""Module with configs with visualisation service."""


class Config(object):
    """Config for visualisation service."""

    url: str = 'http://backend:8000'
    history_load_period: str = '-10m'


config = Config()
