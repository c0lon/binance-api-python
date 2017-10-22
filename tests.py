""" Test suite for the Binance API Client.
"""


import asyncio
import json
import os
import pytest
import random

from binance import (
    BinanceClient,
    configure_app,
    )
from binance.enums import (
    KlineIntervals,
    OrderStatus,
    )
from binance.storage import *


TEST_CONFIG_FILE = 'test_config.yaml'

here = os.path.dirname(os.path.realpath(__file__))
config_uri = os.path.join(here, TEST_CONFIG_FILE)
SETTINGS, GLOBAL_CONFIG = configure_app(config_uri=config_uri)

APIKEY = SETTINGS['apikey']
APISECRET = SETTINGS['apisecret']

ASSETS = [
    'ETH',
]
SYMBOLS = [
    'ETHBTC',
    'LTCBTC',
    'BNBBTC',
    'NEOBTC',
    'OMGBTC',
    'WTCBTC',
]


"""
IDEMPOTENT TESTS
"""


@pytest.mark.skip
def test_ping():
    client = BinanceClient(APIKEY, APISECRET)
    assert client.ping()


@pytest.mark.skip
def test_get_server_time():
    client = BinanceClient(APIKEY, APISECRET)
    assert isinstance(client.get_server_time(), int)


@pytest.mark.skip
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


@pytest.mark.skip
def test_get_ticker():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    ticker = client.get_ticker(symbol)

    assert isinstance(ticker, dict)
    assert ticker['symbol'] == symbol
    assert isinstance(ticker['price'], str)


@pytest.mark.skip
def test_get_ticker_invalid():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = 'DOGE'
    
    try:
        ticker = client.get_ticker(symbol)
    except ValueError as e:
        assert symbol in e.args[0]
    else:
        assert False


def assert_klines(klines):
    assert isinstance(klines, list)
    for kline in klines:
        assert isinstance(kline, list)


@pytest.mark.skip
def test_get_klines():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    klines = client.get_klines(symbol,
            KlineIntervals.THIRTY_MINUTE)
    assert_klines(klines)


@pytest.mark.skip
def test_get_klines_async():
    client = BinanceClient(APIKEY, APISECRET)

    async def klines_callback(klines):
        with open('klines.json', 'w+') as f:
            json.dump(klines, f)

    async def get_klines():
        symbol = random.choice(SYMBOLS)
        klines = await client.get_klines_async(symbol,
                KlineIntervals.ONE_HOUR, callback=klines_callback)
        assert_klines(klines)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_klines())

    with open('klines.json') as f:
        klines_json = json.load(f)
    assert_klines(klines_json)
    os.remove('klines.json')


def assert_depth(depth):
    assert isinstance(depth, dict)
    assert isinstance(depth['bids'], list)
    assert isinstance(depth['asks'], list)


@pytest.mark.skip
def test_get_depth_data():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    depth = client.get_depth(symbol)

    assert_depth(depth)


@pytest.mark.skip
def test_get_depth_data_async():
    client = BinanceClient(APIKEY, APISECRET)

    async def depth_callback(depth):
        with open('depth.json', 'w+') as f:
            json.dump(depth, f)
    
    async def get_depth():
        symbol = random.choice(SYMBOLS)
        depth = await client.get_depth_async(symbol, callback=depth_callback)
        assert_depth(depth)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_depth())

    with open('depth.json') as f:
        depth_json = json.load(f)
    assert_depth(depth_json)
    os.remove('depth.json')


@pytest.mark.skip
def test_get_account_info():
    client = BinanceClient(APIKEY, APISECRET)
    account = client.get_account_info()

    assert isinstance(account, Account)
    for asset, balance in account.balances.items():
        assert isinstance(balance, Balance)
        assert balance.asset == asset


@pytest.mark.skip
def test_get_trade_info():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    trade_info = client.get_trade_info(symbol)

    assert isinstance(trade_info, list)
    for trade in trade_info:
        assert isinstance(trade, Trade)
        assert trade.symbol == symbol


#@pytest.mark.skip
def test_get_open_orders():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    open_orders = client.get_open_orders(symbol)

    assert isinstance(open_orders, list)
    for order in open_orders:
        assert isinstance(order, Order)
        assert order.symbol == symbol


#@pytest.mark.skip
def test_get_all_orders():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = random.choice(SYMBOLS)
    orders = client.get_all_orders(symbol)

    assert isinstance(orders, list)
    for order in orders:
        assert isinstance(order, Order)
        assert order.symbol == symbol


def assert_withdraw(withdraw):
    assert 'address' in withdraw
    assert 'amount' in withdraw
    assert 'applyTime' in withdraw
    assert 'asset' in withdraw
    assert 'status' in withdraw
    if 'successTime' in withdraw:
        assert isinstance(withdraw['successTime'], int)
        assert 'txId' in withdraw


@pytest.mark.skip
def test_get_withdraw_history():
    client = BinanceClient(APIKEY, APISECRET)
    history = client.get_withdraw_history()
    for withdraw in history:
        assert_withdraw(withdraw)


@pytest.mark.skip
def test_get_withdraw_history_asset():
    client = BinanceClient(APIKEY, APISECRET)
    asset = random.choice(ASSETS)

    history = client.get_withdraw_history(asset)
    for withdraw in history:
        assert withdraw['asset'] == asset
        assert_withdraw(withdraw)


def assert_deposit(deposit):
    assert 'amount' in deposit
    assert 'asset' in deposit
    assert 'insertTime' in deposit
    assert 'status' in deposit


@pytest.mark.skip
def test_get_deposit_history():
    client = BinanceClient(APIKEY, APISECRET)
    history = client.get_deposit_history()
    for deposit in history:
        assert_deposit(deposit)


@pytest.mark.skip
def test_get_deposit_history_asset():
    client = BinanceClient(APIKEY, APISECRET)
    asset = random.choice(ASSETS)

    history = client.get_deposit_history(asset)
    for deposit in history:
        assert deposit['asset'] == asset
        assert_deposit(deposit)


"""
ACCOUNT ALTERING TESTS
"""


@pytest.mark.skip
def test_withdraw():
    client = BinanceClient(APIKEY, APISECRET)
    asset = ''
    amount = 0.0
    address = ''

    withdraw = client.withdraw(asset, amount, address)
    assert withdraw


@pytest.mark.skip
def test_place_market_buy():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = ''
    quantity = 0.0
    response = client.place_market_buy(symbol, quantity)

    assert isinstance(response, dict)


@pytest.mark.skip
def test_place_market_sell():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = ''
    quantity = 0.0
    response = client.place_market_sell(symbol, quantity)

    assert isinstance(response, dict)


@pytest.mark.skip
def test_place_limit_buy():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = ''
    quantity = 0.0
    price = 0.0
    response = client.place_limit_buy(symbol, quantity, price)

    assert isinstance(response, dict)


@pytest.mark.skip
def test_place_limit_sell():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = ''
    quantity = 0.0
    price = 0.0
    response = client.place_limit_sell(symbol, quantity, price)

    assert isinstance(response, dict)


@pytest.mark.skip
def test_check_order_status_and_cancel():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = ''
    quantity = 0.0
    price = 0.0
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
