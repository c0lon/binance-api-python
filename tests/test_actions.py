"""
+-------------------------------+
|TEST CONFIGURATION INSTRUCTIONS|
+-------------------------------+

All tests in this file contain variables that will be passed
as parameters to their respective API endpoints. Set these
variables so that you can observe that the tests perform the
actions you expect.

+---------------+
|!!! WARNING !!!|
+---------------+
Your account balances WILL CHANGE if these tests are successful.
Make sure you understand what these tests will do, and that you
are okay with the results.
"""


import time

import pytest

from . import CLIENT
from binance.storage import *
from binance.enums import OrderStatus


"""
TEST WITHDRAW

Set `asset` to the asset you wish to withdraw.
Set `amount` to the amount of `asset` to withdraw.
Set `address` to the address to which you wish to
withdraw your `asset`.

RESULTS IF SUCCESSFUL:
  - Your account will initiate a withdraw `amount` of
    `asset` to `address`.

CONSIDERATIONS:
    Make sure you have at least `quantity` of `asset` in
    your account, or the test will fail.
"""

#@pytest.mark.skip
def test_withdraw():
    asset = ''
    amount = 0.0
    address = ''

    withdraw = CLIENT.withdraw(asset, amount, address)
    assert withdraw


"""
TEST MARKET BUY ORDER

Set `symbol` to the pair you wish to buy at market price.
Set `quantity` to the quantity of your desired market buy.

RESULTS IF SUCCESSFUL:
  - Your account will have place a MARKET BUY ORDER
    for `quantity` of `asset`.

CONSIDERATIONS:
    Make sure you have enough funds for this transaction,
    otherwise the test will fail.

    Since it's a market order, it will likely be filled.
    Make sure you are okay with this.
"""

#@pytest.mark.skip
def test_place_market_buy():
    symbol = ''
    quantity = 0.0

    order = CLIENT.place_market_buy(symbol, quantity)
    assert isinstance(order, Order)
    assert order.symbol == symbol
    assert order.original_quantity == quantity


"""
TEST MARKET SELL ORDER

Set `symbol` to the pair you wish to buy at market price.
Set `quantity` to the quantity of your desired market sell.

RESULTS IF SUCCESSFUL:
  - Your account will have place a MARKET SELL ORDER
    for `quantity` of `asset`.

CONSIDERATIONS:
    Make sure you have enough funds for this transaction,
    otherwise the test will fail.

    Since it's a market order, it will likely be filled.
    Make sure you are okay with this.
"""

#@pytest.mark.skip
def test_place_market_sell():
    symbol = ''
    quantity = 0.0

    order = CLIENT.place_market_sell(symbol, quantity)
    assert isinstance(order, Order)
    assert order.symbol == symbol
    assert order.original_quantity == quantity


"""
TEST LIMIT BUY

Set `symbol` to the pair you wish to buy at a given price.
Set `quantity` to the quantity of your desired limit sell.
Set `price` to the price you at which wish you sell your `symbol`.

RESULTS IF SUCCESSFUL:
  - Your account will have placed a MARKET BUY ORDER
    for `quantity` of `symbol` at `price`.

CONSIDERATIONS:
    If you don't want any actual changes to be made, set
    `price` to something that you are sure will never be filled.
    
    Otherwise, make sure you have enough funds to handle the
    transaction. If not, the test will fail.

    If the test succeeds, be sure to cancel the order
    if you don't want it to be filled.
"""

#@pytest.mark.skip
def test_place_limit_buy():
    symbol = ''
    quantity = 0.0
    price = 0.0

    order = CLIENT.place_limit_buy(symbol, quantity, price)
    assert isinstance(order, Order)
    assert order.symbol == symbol
    assert order.original_quantity == quantity
    assert order.price == price


"""
TEST LIMIT SELL

Set `symbol` to the pair you wish to sell at a given price.
Set `quantity` to the quantity of your desired limit sell.
Set `price` to the price you at which wish you sell your `symbol`.

RESULTS IF SUCCESSFUL:
  - Your account will have placed a MARKET SELL ORDER
    for `quantity` of `symbol` at `price`.

CONSIDERATIONS:
    If you don't want any actual changes to be made, set
    `price` to something that you are sure will never be filled.
    
    Otherwise, make sure you have enough funds to handle the
    transaction. If not, the test will fail.

    If the test succeeds, be sure to cancel the order
    if you don't want it to be filled.
"""

#@pytest.mark.skip
def test_place_limit_sell():
    symbol = ''
    quantity = 0.0
    price = 0.0

    order = CLIENT.place_limit_sell(symbol, quantity, price)
    assert isinstance(order, Order)
    assert order.symbol == symbol
    assert order.original_quantity == quantity
    assert order.price == price


"""
TEST ORDER STATUS + ORDER CANCEL

This test places a LIMIT SELL ORDER, checks its status,
then cancels the order.

Set `symbol` to the pair you wish to sell at a given price.
Set `quantity` to the quantity of your desired limit sell.
Set `price` to the price at which you wish to sell your `symbol`.

RESULTS IF SUCCESSFUL:
  - Your account will place a MARKET SELL ORDER for `quantity` of
    `symbol` at `price`.
  - The API CLIENT will check the status of the order.
  - Your account will cancel the order.
  - The API CLIENT wil once again check the status of the order,
    and ensure that it was cancelled.

CONSIDERATIONS:
    Set `price` to something such that you are sure that the
    order won't be filled immediately. This way, the client
    has time to cancel the order.

    If the order is filled before the client can cancel it,
    the test will fail.
"""

#@pytest.mark.skip
def test_check_order_status_and_cancel():
    symbol = ''
    quantity = 0.0
    price = 0.0

    order = CLIENT.place_limit_sell(symbol, quantity, price)

    time.sleep(1)

    order_status = CLIENT.get_order_status(symbol, order.id)
    assert order_status.id == order.id
    assert order_status.status == OrderStatus.NEW

    assert CLIENT.cancel_order(symbol, order.id)

    order_status = CLIENT.get_order_status(symbol, order.id)
    assert order_status.id == order.id
    assert order_status.status == OrderStatus.CANCELED
