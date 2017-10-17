import random

from binance import BinanceClient

from . import (
    APIKEY,
    APISECRET,
    )


SYMBOLS = [
    'ETHBTC',
    'LTCBTC',
    'BNBBTC',
    'NEOBTC',
    'OMGBTC',
    'WTCBTC',
]


def test_get_ticker_all():
    client = BinanceClient(APIKEY, APISECRET)
    ticker_data = client.get_ticker()

    assert random.choice(SYMBOLS) in ticker_data
    assert isinstance(ticker_data[random.choice(SYMBOLS)], float)

def test_get_ticker():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    price = client.get_ticker(symbol)

    assert isinstance(price, float)

