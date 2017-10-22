""" Test suite for the Binance API Client.
"""


import asyncio
from datetime import datetime
import json
import os
import pytest
import random

from binance.enums import (
    KlineIntervals,
    OrderStatus,
    )
from binance.storage import *

from . import (
    APIKEY,
    APISECRET,
    ASSETS,
    CLIENT,
    SYMBOLS,
    )


#@pytest.mark.skip
def test_ping():
    assert CLIENT.ping()


#@pytest.mark.skip
def test_get_server_time():
    assert isinstance(CLIENT.get_server_time(), int)


def assert_ticker(ticker):
    assert isinstance(ticker, Ticker)
    assert isinstance(ticker.symbol, str)
    assert isinstance(ticker.price, float)


#@pytest.mark.skip
def test_get_ticker():
    tickers = CLIENT.get_ticker()

    assert isinstance(tickers, list)
    symbols = set()
    for ticker in tickers:
        assert_ticker(ticker)
        symbols.add(ticker.symbol)

    for symbol in SYMBOLS:
        assert symbol in symbols


#@pytest.mark.skip
def test_get_ticker_symbol():
    symbol = random.choice(SYMBOLS)
    ticker = CLIENT.get_ticker(symbol)

    assert ticker.symbol == symbol
    assert_ticker(ticker)


#@pytest.mark.skip
def test_get_ticker_invalid():
    symbol = 'DOGE'
    
    try:
        ticker = CLIENT.get_ticker(symbol)
    except ValueError as e:
        assert e.args[0] == f'invalid symbol: {symbol}'
    else:
        assert False


def assert_klines(klines):
    assert isinstance(klines, list)
    for kline in klines:
        assert isinstance(kline, list)


#@pytest.mark.skip
def test_get_klines():
    symbol = random.choice(SYMBOLS)
    klines = CLIENT.get_klines(symbol,
            KlineIntervals.THIRTY_MINUTE)
    assert_klines(klines)


#@pytest.mark.skip
def test_get_klines_async():
    async def klines_callback(klines):
        with open('klines.json', 'w+') as f:
            json.dump(klines, f)

    async def get_klines():
        symbol = random.choice(SYMBOLS)
        klines = await CLIENT.get_klines_async(symbol,
                KlineIntervals.ONE_HOUR, callback=klines_callback)
        assert_klines(klines)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_klines())

    with open('klines.json') as f:
        klines_json = json.load(f)
    assert_klines(klines_json)
    os.remove('klines.json')


def assert_depth(depth):
    assert isinstance(depth, Depth)
    assert isinstance(depth.update_id, int)

    for bid in depth.bids:
        assert isinstance(bid, Bid)
        assert isinstance(bid.price, float)
        assert isinstance(bid.quantity, float)

    for ask in depth.asks:
        assert isinstance(ask, Ask)
        assert isinstance(ask.price, float)
        assert isinstance(ask.quantity, float)


#@pytest.mark.skip
def test_get_depth_data():
    symbol = random.choice(SYMBOLS)
    depth = CLIENT.get_depth(symbol)

    assert depth.symbol == symbol
    assert_depth(depth)


#@pytest.mark.skip
def test_get_depth_data_async():
    symbol = random.choice(SYMBOLS)

    async def depth_callback(depth):
        with open('depth.json', 'w+') as f:
            json.dump(depth.to_json(), f)
    
    async def get_depth():
        depth = await CLIENT.get_depth_async(symbol, callback=depth_callback)
        assert depth.symbol == symbol
        assert_depth(depth)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_depth())

    with open('depth.json') as f:
        depth_json = json.load(f)
    assert depth_json['symbol'] == symbol
    assert isinstance(depth_json['update_id'], int)
    assert isinstance(depth_json['bids'], list)
    assert isinstance(depth_json['asks'], list)
    os.remove('depth.json')


#@pytest.mark.skip
def test_get_account_info():
    account = CLIENT.get_account_info()

    assert isinstance(account, Account)
    for asset, balance in account.balances.items():
        assert isinstance(balance, Balance)
        assert balance.asset == asset


#@pytest.mark.skip
def test_get_trade_info():
    symbol = random.choice(SYMBOLS)
    trade_info = CLIENT.get_trade_info(symbol)

    assert isinstance(trade_info, list)
    for trade in trade_info:
        assert isinstance(trade, Trade)
        assert trade.symbol == symbol


#@pytest.mark.skip
def test_get_open_orders():
    symbol = random.choice(SYMBOLS)
    open_orders = CLIENT.get_open_orders(symbol)

    assert isinstance(open_orders, list)
    for order in open_orders:
        assert isinstance(order, Order)
        assert order.symbol == symbol


#@pytest.mark.skip
def test_get_all_orders():
    symbol = random.choice(SYMBOLS)
    orders = CLIENT.get_all_orders(symbol)

    assert isinstance(orders, list)
    for order in orders:
        assert isinstance(order, Order)
        assert order.symbol == symbol


def assert_withdraw(withdraw):
    assert isinstance(withdraw, Withdraw)
    assert isinstance(withdraw.apply_time, datetime)
    if withdraw.success_time:
        assert isinstance(withdraw.success_time, datetime)
        assert withdraw.tx_id


#@pytest.mark.skip
def test_get_withdraw_history():
    history = CLIENT.get_withdraw_history()
    for withdraw in history:
        assert_withdraw(withdraw)


#@pytest.mark.skip
def test_get_withdraw_history_asset():
    asset = random.choice(ASSETS)

    history = CLIENT.get_withdraw_history(asset)
    for withdraw in history:
        assert withdraw.asset == asset
        assert_withdraw(withdraw)


def assert_deposit(deposit):
    assert isinstance(deposit, Deposit)
    if deposit.insert_time:
        assert isinstance(deposit.insert_time, datetime)


#@pytest.mark.skip
def test_get_deposit_history():
    history = CLIENT.get_deposit_history()
    for deposit in history:
        assert_deposit(deposit)


#@pytest.mark.skip
def test_get_deposit_history_asset():
    asset = random.choice(ASSETS)

    history = CLIENT.get_deposit_history(asset)
    for deposit in history:
        assert deposit.asset == asset
        assert_deposit(deposit)
