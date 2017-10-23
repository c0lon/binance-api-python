""" Test suite for the Binance API Client.
"""


import asyncio
from datetime import datetime
import json
import os
import pytest
import random

from binance.enums import (
    CandlestickIntervals,
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

    ticker_json = ticker.to_json()
    assert ticker_json['symbol'] == ticker.symbol
    assert ticker_json['price'] == ticker.price


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


def assert_candlestick(candlestick):
    assert isinstance(candlestick, Candlestick)
    assert isinstance(candlestick.price, CandlestickPrice)
    assert candlestick.price.high >= candlestick.price.low

    assert isinstance(candlestick.open_time, datetime)
    assert isinstance(candlestick.close_time, datetime)
    assert candlestick.close_time > candlestick.open_time

    candlestick_json = candlestick.to_json()
    assert candlestick_json['price'] == candlestick.price.to_json()
    assert datetime.fromtimestamp(candlestick_json['open_time']) == candlestick.open_time
    assert datetime.fromtimestamp(candlestick_json['close_time']) == candlestick.close_time


#@pytest.mark.skip
def test_get_candlesticks():
    symbol = random.choice(SYMBOLS)
    candlesticks = CLIENT.get_candlesticks(symbol,
            CandlestickIntervals.THIRTY_MINUTE)

    for candlestick in candlesticks:
        assert_candlestick(candlestick)


#@pytest.mark.skip
def test_get_candlesticks_async():
    symbol = random.choice(SYMBOLS)

    async def candlesticks_callback(candlesticks):
        candlesticks_json = [c.to_json() for c in candlesticks]
        with open('candlesticks.json', 'w+') as f:
            json.dump(candlesticks_json, f)

    async def get_candlesticks():
        candlesticks = await CLIENT.get_candlesticks_async(symbol,
                CandlestickIntervals.ONE_HOUR, callback=candlesticks_callback)
        for candlestick in candlesticks:
            assert candlestick.symbol == symbol
            assert_candlestick(candlestick)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_candlesticks())

    with open('candlesticks.json') as f:
        candlesticks_json = json.load(f)
    for candlestick in candlesticks_json:
        assert candlestick['symbol'] == symbol
    os.remove('candlesticks.json')


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

    depth_json = depth.to_json()
    assert depth_json['symbol'] == depth.symbol
    assert depth_json['update_id'] == depth.update_id
    for i, bid_json in enumerate(depth_json['bids']):
        assert bid_json == depth.bids[i].to_json()
    for i, ask_json in enumerate(depth_json['asks']):
        assert ask_json == depth.asks[i].to_json()


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

        balance_json = balance.to_json()
        assert balance_json['asset'] == balance.asset
        assert balance_json['free'] == balance.free
        assert balance_json['locked'] == balance.locked


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

    withdraw_json = withdraw.to_json()
    assert withdraw_json['asset'] == withdraw.asset
    assert datetime.fromtimestamp(withdraw_json['apply_time']) == withdraw.apply_time
    if withdraw.success_time:
        assert datetime.fromtimestamp(withdraw_json['success_time']) == withdraw.success_time


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

    deposit_json = deposit.to_json()
    assert deposit_json['asset'] == deposit.asset
    assert deposit_json['amount'] == deposit.amount
    assert deposit_json['status'] == deposit.status
    if deposit.insert_time:
        assert datetime.fromtimestamp(deposit_json['insert_time']) == deposit.insert_time


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
