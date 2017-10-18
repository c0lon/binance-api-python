import asyncio
import pytest
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


#@pytest.mark.skip
def test_get_ticker_all():
    client = BinanceClient(APIKEY, APISECRET)
    ticker_data = client.get_ticker()

    assert random.choice(SYMBOLS) in ticker_data
    assert isinstance(ticker_data[random.choice(SYMBOLS)], float)


#@pytest.mark.skip
def test_get_ticker():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    price = client.get_ticker(symbol)

    assert isinstance(price, float)


#@pytest.mark.skip
def test_get_depth_data():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    depth = client.get_depth(symbol)

    assert isinstance(depth, dict)
    assert isinstance(depth['bids'], list)
    assert isinstance(depth['asks'], list)


#@pytest.mark.skip
def test_get_account_info():
    client = BinanceClient(APIKEY, APISECRET)
    account_info = client.get_account_info()

    assert isinstance(account_info, dict)
