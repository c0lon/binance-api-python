""" Test suite for the Binance API Client.
"""


import asyncio
import pytest
import random

from binance import BinanceClient
from binance.client import OrderStatus

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
    ticker = client.get_ticker()

    assert isinstance(ticker, list)

    symbols = []
    for symbol_ticker in ticker:
        assert isinstance(symbol_ticker, dict)
        assert isinstance(symbol_ticker['price'], str)
        symbols.append(symbol_ticker['symbol'])

    for symbol in SYMBOLS:
        assert symbol in symbols


#@pytest.mark.skip
def test_get_ticker():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    ticker = client.get_ticker(symbol)

    assert isinstance(ticker, dict)
    assert ticker['symbol'] == symbol
    assert isinstance(ticker['price'], str)


#@pytest.mark.skip
def test_get_ticker_invalid():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = 'DOGE'
    
    try:
        ticker = client.get_ticker(symbol)
    except ValueError as e:
        assert symbol in e.args[0]
    else:
        assert False


def assert_depth(depth):
    assert isinstance(depth, dict)
    assert isinstance(depth['bids'], list)
    assert isinstance(depth['asks'], list)


#@pytest.mark.skip
def test_get_depth_data():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    depth = client.get_depth(symbol)

    assert_depth(depth)


#@pytest.mark.skip
def test_get_depth_data_async():
    client = BinanceClient(APIKEY, APISECRET)
    
    async def get_depth():
        symbol = random.choice(SYMBOLS)
        depth = await client.get_depth_async(symbol)
        assert_depth(depth)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_depth())


#@pytest.mark.skip
def test_get_account_info():
    client = BinanceClient(APIKEY, APISECRET)
    account_info = client.get_account_info()

    assert isinstance(account_info, dict)


#@pytest.mark.skip
def test_get_trade_info():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    trade_info = client.get_trade_info(symbol)

    assert isinstance(trade_info, list)


#@pytest.mark.skip
def test_get_open_orders():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    open_orders = client.get_open_orders(symbol)

    assert isinstance(open_orders, list)


#@pytest.mark.skip
def test_get_all_orders():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    open_orders = client.get_all_orders(symbol)

    assert isinstance(open_orders, list)


@pytest.mark.skip
def test_place_market_buy():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = SYMBOLS[0]
    quantity = 0.5
    response = client.place_market_buy(symbol, quantity)

    assert isinstance(response, dict)


@pytest.mark.skip
def test_place_market_sell():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = SYMBOLS[0]
    quantity = 0.05
    response = client.place_market_sell(symbol, quantity)

    assert isinstance(response, dict)


@pytest.mark.skip
def test_place_limit_buy():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = SYMBOLS[0]
    quantity = 1.0
    price = 0.001
    response = client.place_limit_buy(symbol, quantity, price)

    assert isinstance(response, dict)


@pytest.mark.skip
def test_place_limit_sell():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = SYMBOLS[0]
    quantity = 0.05
    price = 1.0
    response = client.place_limit_sell(symbol, quantity, price)

    assert isinstance(response, dict)


@pytest.mark.skip
def test_check_order_status_and_cancel():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = SYMBOLS[0]
    quantity = 0.05
    price = 1.0
    order_response = client.place_limit_sell(symbol, quantity, price)
    order_id = order_response['orderId']

    order_status_response = client.get_order_status(symbol, order_id)
    assert order_status_response['orderId'] == order_id
    assert order_status_response['status'] == OrderStatus.NEW

    order_cancel_response = client.cancel_order(symbol, order_id)
    assert order_cancel_response['orderId'] == order_id

    order_status_response = client.get_order_status(symbol, order_id)
    assert order_status_response['orderId'] == order_id
    assert order_status_response['status'] == OrderStatus.CANCELED
