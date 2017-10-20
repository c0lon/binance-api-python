""" DepthCache helper class for the Binance API Client.
"""


from collections import deque

from .utils import GetLoggerMixin


class DepthCache(GetLoggerMixin):
    __loggername__ = 'DepthCache'

    def __init__(self):
        self.bids = []
        self.asks = []

        self.received_api_response = False
        self.event_queue = deque()
        self.last_update_id = -1

    def update(self, event):
        if not self.received_api_response:
            self.event_queue.append(event)
        else:
            self._update(event)

    def _transform_depth(self, depth):
        return {price: quantity for price, quantity, _ in depth}

    def _update(self, event):
        logger = self._logger('_update')

        if event['u'] < self.last_update_id: return
        logger.debug(event['u'])

        self.last_update_id = event['u']
        event_bids = self._transform_depth(event['b'])
        event_asks = self._transform_depth(event['a'])

        updated_bids = []
        for bid_price, bid_quantity in self.bids:
            updated_bid_quantity = event_bids.get(bid_price, bid_quantity)
            if not float(updated_bid_quantity): continue
            updated_bids.append([bid_price, updated_bid_quantity])
        self.bids = updated_bids

        updated_asks = []
        for ask_price, ask_quantity in self.asks:
            updated_ask_quantity = event_asks.get(ask_price, ask_quantity)
            if not float(updated_ask_quantity): continue
            updated_asks.append([ask_price, updated_ask_quantity])
        self.asks = updated_asks

    def set_initial_data(self, depth):
        logger = self._logger('set_initial_data')

        self.last_update_id = depth['lastUpdateId']
        logger.debug(f'set_initial_data: {self.last_update_id}')

        self.bids = [b[:2] for b in depth['bids']]
        self.asks = [a[:2] for a in depth['asks']]
        while self.event_queue:
            event = self.event_queue.popleft()
            self._update(event)

        self.received_api_response = True

    def pretty_print(self, depth=40):
        if depth:
            d = int(depth/2)
            bids = self.bids[:d]
            asks = self.asks[-d:]
        else:
            bids = self.bids
            asks = self.asks

        print('Bids')
        for bid_price, bid_quantity in bids:
            print(f'{float(bid_price):12f} : {float(bid_quantity):12f}')

        print('\nAsks')
        for ask_price, ask_quantity in asks:
            print(f'{float(ask_price):12f} : {float(ask_quantity):12f}')
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
