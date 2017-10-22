from datetime import datetime

from .enums import (
    OrderSides,
    OrderTypes,
    )
from .utils import pp


class Account:
    def __init__(self, raw_account):
        self.maker_commission = raw_account['makerCommission']
        self.taker_commission = raw_account['takerCommission']
        self.buyer_commission = raw_account['buyerCommission']
        self.seller_commission = raw_account['sellerCommission']

        self.can_trade = raw_account['canTrade']
        self.can_withdraw = raw_account['canWithdraw']
        self.canDeposit = raw_account['canDeposit']

        self.balances = {}
        for balance in raw_account['balances']:
            self.balances[balance['asset']] = Balance(balance)


class Balance:
    def __init__(self, raw_balance):
        self.asset = raw_balance['asset']
        self.free = float(raw_balance['free'])
        self.locked = float(raw_balance['locked'])


class Order:
    def __init__(self, raw_order):
        self.id = raw_order['orderId']
        self.symbol = raw_order['symbol']
        self.client_order_id = raw_order['clientOrderId']
        self.price = float(raw_order['price'])
        self.original_quantity = float(raw_order['origQty'])
        self.executed_quantity = float(raw_order['executedQty'])
        self.status = raw_order['status']
        self.time_in_force = raw_order['timeInForce']
        self.type = getattr(OrderTypes, raw_order['type'])
        self.side = getattr(OrderSides, raw_order['side'])
        self.stop_price = float(raw_order['stopPrice']) or None
        self.icebergQuantity = float(raw_order['icebergQty']) or None
        self.time = raw_order['time']


class Trade:
    def __init__(self, symbol, raw_trade):
        self.symbol = symbol
        self.id = raw_trade['id']
        self.price = float(raw_trade['price'])
        self.quantity = float(raw_trade['qty'])
        self.commission = float(raw_trade['commission'])
        self.commission_asset = float(raw_trade['commissionAsset'])
        self.time = raw_trade['time']
        self.isBuyer = raw_trade['isBuyer']
        self.isMaker = raw_trade['isMaker']
        self.isBestMatch = raw_trade['isBestMatch']


class Deposit:
    def __init__(self, raw_deposit):
        self.asset = raw_deposit['asset']
        self.amount = raw_deposit['amount']
        self.status = raw_deposit['status']

        self.insert_time = raw_deposit.get('insertTime')
        if self.insert_time:
            self.insert_time = datetime.fromtimestamp(self.insert_time / 1000)


class Withdraw:
    def __init__(self, raw_withdraw):
        self.asset = raw_withdraw['asset']
        self.status = raw_withdraw['status']
        self.amount = raw_withdraw['amount']
        self.address = raw_withdraw['address']
        self.tx_id = raw_withdraw.get('txId')

        apply_time = raw_withdraw['applyTime'] / 1000
        self.apply_time = datetime.fromtimestamp(apply_time)

        self.success_time = raw_withdraw.get('successTime')
        if self.success_time:
            self.success_time = datetime.fromtimestamp(self.success_time / 1000)
