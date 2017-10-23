from copy import deepcopy
from datetime import datetime

from .enums import (
    OrderSides,
    OrderTypes,
    )


class Ticker:
    def __init__(self, raw_ticker):
        self.symbol = raw_ticker['symbol']
        self.price = float(raw_ticker['price'])

    def to_json(self):
        return deepcopy(self.__dict__)


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

    def to_json(self):
        j = deepcopy(self.__dict__)
        for asset in self.balances:
            j['balances'][asset] = self.banaces[asset].to_json()

        return j


class Balance:
    def __init__(self, raw_balance):
        self.asset = raw_balance['asset']
        self.free = float(raw_balance['free'])
        self.locked = float(raw_balance['locked'])

    def to_json(self):
        return deepcopy(self.__dict__)


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

    def to_json(self):
        return deepcopy(self.__dict__)


class Trade:
    def __init__(self, symbol, raw_trade):
        self.symbol = symbol
        self.id = raw_trade['id']
        self.price = float(raw_trade['price'])
        self.quantity = float(raw_trade['qty'])
        self.commission = float(raw_trade['commission'])
        self.commission_asset = raw_trade['commissionAsset']
        self.time = raw_trade['time']
        self.isBuyer = raw_trade['isBuyer']
        self.isMaker = raw_trade['isMaker']
        self.isBestMatch = raw_trade['isBestMatch']

    def to_json(self):
        return deepcopy(self.__dict__)


class Depth:
    def __init__(self, symbol, raw_depth):
        self.symbol = symbol
        self.update_id = raw_depth['lastUpdateId']
        self.bids = [Bid(b) for b in raw_depth['bids']]
        self.asks = [Ask(a) for a in raw_depth['asks']]

    def to_json(self):
        return {
            'symbol' : self.symbol,
            'update_id' : self.update_id,
            'bids' : [b.to_json() for b in self.bids],
            'asks' : [a.to_json() for a in self.asks]
        }


class Bid:
    def __init__(self, raw_bid):
        self.price = float(raw_bid[0])
        self.quantity = float(raw_bid[1])

    def to_json(self):
        return deepcopy(self.__dict__)


class Ask:
    def __init__(self, raw_ask):
        self.price = float(raw_ask[0])
        self.quantity = float(raw_ask[1])

    def to_json(self):
        return deepcopy(self.__dict__)


class Candlestick:
    def __init__(self, symbol, raw_candlestick):
        self.symbol = symbol

        self.open_time = datetime.fromtimestamp(raw_candlestick[0] / 1000)
        self.close_time = datetime.fromtimestamp(raw_candlestick[6] / 1000)

        self.price = CandlestickPrice(*raw_candlestick[1:5])
        self.volume = float(raw_candlestick[5])
        self.quote_asset_volume = float(raw_candlestick[7])
        self.trades = raw_candlestick[8]
        self.taker_buy_base_asset_volume = raw_candlestick[9]
        self.taker_buy_quote_asset_volume = raw_candlestick[10]

    @classmethod
    def from_websocket_event(cls, symbol, event):
        transformed_event = [
            event['k']['t'], # open time
            event['k']['o'], # open price
            event['k']['h'], # high price
            event['k']['l'], # low price
            event['k']['c'], # close price
            event['k']['v'], # volume
            event['k']['T'], # close time
            event['k']['q'], # quote asset volume ?
            event['k']['n'], # trades
            event['k']['V'], # taker buy base asset volume ?
            event['k']['Q']  # taker buy quote asset volume ?
        ]

        return cls(symbol, transformed_event)

    def to_json(self):
        j = deepcopy(self.__dict__)
        j['open_time'] = self.open_time.timestamp()
        j['close_time'] = self.close_time.timestamp()
        j['price'] = j['price'].to_json()

        return j


class CandlestickPrice:
    def __init__(self, open_, high, low, close):
        self.open = open_
        self.high = high
        self.low = low
        self.close = close

    def to_json(self):
        return deepcopy(self.__dict__)


class Deposit:
    def __init__(self, raw_deposit):
        self.asset = raw_deposit['asset']
        self.amount = raw_deposit['amount']
        self.status = raw_deposit['status']

        self.insert_time = raw_deposit.get('insertTime')
        if self.insert_time:
            self.insert_time = datetime.fromtimestamp(self.insert_time / 1000)

    def to_json(self):
        j = deepcopy(self.__dict__)
        if self.insert_time:
            j['insert_time'] = self.insert_time.timestamp()

        return j


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

    def to_json(self):
        j = deepcopy(self.__dict__)
        j['apply_time'] = self.apply_time.timestamp()
        if self.success_time:
            j['success_time'] = self.success_time.timestamp()

        return j
