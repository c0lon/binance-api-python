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


class CandlestickCache(GetLoggerMixin):
    __loggername__ = 'CandlestickCache'

    def __init__(self):
        self.candlesticks = []
        self.received_api_response = False
        self.depth = 0

    def update(self, event):
        if self.received_api_response:
            self._update(event)

    def _update(self, event):
        logger = self._logger('_update')

        event_candlestick = Candlestick.from_websocket_event(event)
        latest_candlestick = self.candlesticks[-1]

        # if the event candlestick has the same time window
        # as the latest candlestick, update the latest candlestick
        # 
        # if the event candlestick is of a newer time window
        # than the latest candlestick, add it to the list
        # keep candlestick list a certain length
        if event_candlestick.open_time == latest_candlestick.open_time:
            self.candlesticks[-1] = event_candlestick
        elif event_candlestick.open_time > latest_candlestick.open_time:
            self.candlesticks.append(event_candlestick)
            if len(self.candlesticks) > self.depth:
                self.candlesticks.pop(0)

    def set_initial_data(self, candlesticks):
        self._logger().info('set_initial_data')

        self.candlesticks = candlesticks
        self.depth = len(self.candlesticks)
        self.received_api_response = True

    def pretty_print(self, depth=40):
        if depth:
            candlesticks = self.candlesticks[-depth:]
        else:
            candlesticks = self.candlesticks

        for candlestick in candlesticks:
            date_string = candlestick.open_time.strftime('%Y-%m-%d %H:%M:%S')
            print(f'{candlestick.symbol} {date_string}')
            print(f'      open: {candlestick.price.open}')
            print(f'      high: {candlestick.price.high}')
            print(f'       low: {candlestick.price.low}')
            print(f'     close: {candlestick.price.low}')
            print(f'    volume: {candlestick.volume}')
            print()
