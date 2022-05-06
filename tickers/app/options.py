import json


def read_tickers(tickers_file: str) -> list:
    """
    Read tickers from initial.
    """
    with open(tickers_file) as tf:
        tickers = json.loads(tf.read())
        return tickers
