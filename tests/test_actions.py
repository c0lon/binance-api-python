from . import (
    APIKEY,
    APISECRET,
    )
from binance import BinanceClient
from binance.storage import *


#@pytest.mark.skip
def test_withdraw():
    client = BinanceClient(APIKEY, APISECRET)
    asset = ''
    amount = 0.0
    address = ''

    withdraw = client.withdraw(asset, amount, address)
    assert withdraw


#@pytest.mark.skip
def test_place_market_buy():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = ''
    quantity = 0.0
    response = client.place_market_buy(symbol, quantity)

    assert isinstance(response, dict)


#@pytest.mark.skip
def test_place_market_sell():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = ''
    quantity = 0.0
    response = client.place_market_sell(symbol, quantity)

    assert isinstance(response, dict)


#@pytest.mark.skip
def test_place_limit_buy():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = ''
    quantity = 0.0
    price = 0.0
    response = client.place_limit_buy(symbol, quantity, price)

    assert isinstance(response, dict)


#@pytest.mark.skip
def test_place_limit_sell():
    client = BinanceClient(APIKEY, APISECRET)
    symbol = ''
    quantity = 0.0
    price = 0.0
    response = client.place_limit_sell(symbol, quantity, price)

    assert isinstance(response, dict)


#@pytest.mark.skip
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
