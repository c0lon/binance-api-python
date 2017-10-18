import asyncio

import websockets as ws

from .client import BinanceClient


WEBSOCKET_BASE_URL = 'wss://stream.binance.com:9443/ws/{symbol}'
DEPTH_WEBSOCKET_URL = '{}@depth'.format(WEBSOCKET_BASE_URL)
KLINE_WEBSOCKET_URL = '{}@kline'.format(WEBSOCKET_BASE_URL)


class EventCache:
    def __init__(self, symbol):
        self.symbol = symbol
        self.depths = []

    def watch_depth(self):
        pass

    def watch_klines(self):
        pass


async def watch_depth(apikey, apisecret, symbol):
    client = BinanceClient(apikey, apisecret)
    cache = EventCache(symbol)

    with ws.connect(DEPTH_WEBSOCKET_URL.format(symbol)) as socket:
        cache.watch(symbol, socket)
        api_response = await client.get_depth_async(symbol)


async def watch_klines(symbol):
    pass
