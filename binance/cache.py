""" DepthCache helper class for the Binance API Client.
"""


from collections import deque

from .storage import (
    Bid,
    Ask,
    )
from .utils import GetLoggerMixin


class DepthCache(GetLoggerMixin):
    __loggername__ = 'DepthCache'

    def __init__(self):
        self.bids = []
        self.asks = []

        self.received_api_response = False
        self.event_queue = deque()
        self.last_update_id = -1

    def _update(self, event):
        logger = self._logger('_update')

        if event['u'] < self.last_update_id: return
        logger.debug(event['u'])

        self.last_update_id = event['u']
        event_bids = {b[0]: Bid(b) for b in event['bids']}
        event_asks = {a[0]: Ask(a) for a in event['asks']}

        updated_bids = []
        for bid in self.bids:
            event_bid = event_bids.get(bid.price)
            if not event_bid:
                updated_asks.append(ask)
            elif not event_bid.quantity:
                continue
            else:
                updates_bids.append(event_bid)
        self.bids = updated_bids

        updated_asks = []
        for ask in self.asks:
            event_ask = event_asks.get(ask.price)
            if not event_ask:
                updated_asks.append(ask)
            elif not event_ask.quantity:
                continue
            else:
                updated_asks.append(ask)
        self.asks = updated_asks

    def set_initial_data(self, depth):
        logger = self._logger('set_initial_data')

        self.last_update_id = depth.update_id
        logger.debug(f'set_initial_data: {self.last_update_id}')

        self.bids = depth.bids
        self.asks = depth.asks
        while self.event_queue:
            event = self.event_queue.popleft()
            self._update(event)

        self.received_api_response = True

    def pretty_print(self, depth=40):
        if depth:
            bids = self.bids[:depth]
            asks = self.asks[:depth]
        else:
            bids = self.bids
            asks = self.asks

        print('Bids')
        for bid in bids:
            print(f'{bid.price:12f} : {bid.quantity:12f}')

        print('\nAsks')
        for ask in asks:
            print(f'{ask.price:12f} : {ask.quantity:12f}')
        print()


class KlineCache(GetLoggerMixin):
    __loggername__ = 'KlineCache'

    def __init__(self):
        self.klines = []
        self.received_api_response = False
        self.depth = 0

    def update(self, event):
        if self.received_api_response:
            self._update(event)

    def _update(self, event):
        logger = self._logger('_update')

        event_kline = self._transform_event(event)
        latest_kline = self.klines[-1]
        if event['E'] != latest_kline[0]:
            self.klines.append((event['E'], event_kline))
            if len(self.klines) > self.depth:
                self.klines.pop(0)

    def _transform_event(self, event):
        return {
            'open' : event['k']['o'],
            'high' : event['k']['h'],
            'low' : event['k']['l'],
            'close' : event['k']['c'],
            'volume' : event['k']['v']
        }

    def set_initial_data(self, klines):
        self._logger().info('set_initial_data')

        for kline in klines:
            transformed_kline = self._transform_kline(kline)
            self.klines.append((kline[0], transformed_kline))
        self.depth = len(self.klines)
        self.received_api_response = True

    def _transform_kline(self, kline):
        return {
            'open' : kline[1],
            'high' : kline[2],
            'low' : kline[3],
            'close' : kline[4],
            'volume' : kline[5]
        }

    def pretty_print(self, depth=40):
        if depth:
            klines = self.klines[-depth:]
        else:
            klines = self.klines

        for kline_timestamp, kline in klines:
            print(f'timestamp: {kline_timestamp}')
            print(f'    open: {kline["open"]}')
            print(f'    high: {kline["high"]}')
            print(f'    low: {kline["low"]}')
            print(f'    close: {kline["close"]}')
            print(f'    volume: {kline["volume"]}')
            print()
