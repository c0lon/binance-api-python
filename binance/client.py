import asyncio
import hashlib
import hmac
import json
import time
from urllib.parse import (
    quote,
    urljoin,
    )

import aiohttp
import requests
import websockets as ws

from .cache import DepthCache
from .utils import GetLoggerMixin


API_BASE_URL = 'https://www.binance.com/api'

WEBSOCKET_BASE_URL = 'wss://stream.binance.com:9443/ws/{symbol}'
DEPTH_WEBSOCKET_URL = '{}@depth'.format(WEBSOCKET_BASE_URL)

CONTENT_TYPE = 'x-www-form-urlencoded'


class Endpoints:
    ACCOUNT_INFO = 'account'
    TRADE_INFO = 'myTrades'
    ORDER = 'order'
    ALL_ORDERS = 'allOrders'
    OPEN_ORDERS = 'openOrders'
    TICKER = 'ticker/allPrices'
    DEPTH = 'depth'

class Sides:
    BUY = 'BUY'
    SELL = 'SELL'

class OrderTypes:
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'

class OrderStatus:
    NEW = 'NEW'
    CANCELED = 'CANCELED'
    PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    FILLED = 'FILLED'
    PENDING_CANCEL = 'PENDING_CANCEL'
    REJECTED = 'REJECTED'
    EXPIRED = 'EXPIRED'

class TimeInForce:
    GTC = 'GTC'
    IOC = 'IOC'


class BinanceClient(GetLoggerMixin):
    __loggername__ = 'BinanceClient'

    def __init__(self, apikey, apisecret):
        if not apikey or not apisecret:
            self._logger().error('invalid api key/secret')
            raise ValueError('invalid api key/secret')

        self.apikey = apikey
        self.apisecret = apisecret
        self.headers = {
                'X-MBX-APIKEY' : self.apikey,
                'content_type' : CONTENT_TYPE
                }

        self._loop = asyncio.get_event_loop()
        self.depth_cache = {}

    def _prepare_request(self, path, verb, params, signed):
        params = params or {}

        if signed:
            url = self._sign_request(path, params)
        elif params:
            query_string = self._get_sorted_query_string(params)
            url = '{}/v1/{}?{}'.format(API_BASE_URL, path, query_string)
        else:
            url = '{}/v1/{}'.format(API_BASE_URL, path)

        return url

    def _make_request(self, path, verb='get', params=None, signed=False):
        logger = self._logger('_make_request')

        verb = verb.lower()
        url = self._prepare_request(path, verb, params, signed)
        logger.info(f'{verb.upper()} {url}')

        http_function = getattr(requests, verb)
        response = http_function(url, headers=self.headers)
        response_json = response.json()

        if response.ok:
            return response.json()

        # don't overwrite 'msg' in log record
        response_json['error'] = response_json.pop('msg')
        logger.error(f'error: {response.reason}', exc_info=True)
        logger.debug(response_json['error'], extra=response_json)

        raise response.raise_for_status()

    async def _make_request_async(self, path, verb='get', params=None, signed=False):
        logger = self._logger('_make_request_async')

        verb = verb.lower()
        url = self._prepare_request(path, verb, params, signed)
        logger.info(f'{verb.upper()} {url}')

        async with aiohttp.ClientSession() as client:
            http_function = getattr(client, verb)
            response = await http_function(url, headers=self.headers)

            response_json = await response.json(content_type=None)
            if response.reason == 'OK':
                logger.debug('success', extra=response_json)
                return response_json

            # don't overwrite 'msg' in log record
            response_json['error'] = response_json.pop('msg')
            logger.error(f'error: {response.reason}', exc_info=True)
            logger.debug(response_json['error'], extra=response_json)

            response.raise_for_status()

    def _get_sorted_query_string(self, params):
        sorted_parameters = []
        for param in sorted(params.keys()):
            url_encoded_value = quote(str(params[param]))
            sorted_parameters.append('{}={}'.format(param, url_encoded_value))

        return '&'.join(sorted_parameters)

    def _sign_request(self, path, params):
        url = '{}/v3/{}'.format(API_BASE_URL, path)

        params['timestamp'] = int(round(time.time() * 1000.0))
        if 'recvWindow' not in params: params['recvWindow'] = 6000
        query_string = self._get_sorted_query_string(params)

        signature = hmac.new(
                self.apisecret.encode(),
                digestmod=hashlib.sha256)
        signature.update(query_string.encode())

        return '{}?{}&signature={}'.format(
                url, query_string, signature.hexdigest())

    def get_ticker(self, symbol=''):
        self._logger('get_ticker').info(symbol)
        ticker = self._make_request(Endpoints.TICKER)

        if symbol:
            for _symbol in ticker:
                if _symbol['symbol'] == symbol:
                    return _symbol
            else:
                raise ValueError('invalid symbol: {}'.format(symbol))

        return ticker

    def get_depth(self, symbol):
        self._logger('get_depth').info(symbol)
        return self._make_request(Endpoints.DEPTH, params={'symbol' : symbol})

    async def get_depth_async(self, symbol):
        self._logger('get_depth_async').info(symbol)
        return await self._make_request_async(Endpoints.DEPTH,
                params={'symbol': symbol})

    def watch_depth(self, symbol):
        self._logger('watch_depth').info(symbol)

        cache = self.depth_cache.get(symbol)
        if not cache:
            cache = DepthCache()
            self.depth_cache[symbol] = cache

        async def _watch_for_depth_events():
            logger = self._logger('_watch_for_depth_events')

            url = DEPTH_WEBSOCKET_URL.format(symbol=symbol.lower())
            async with ws.connect(url) as socket:
                while True:
                    event = await socket.recv()
                    try:
                        event_dict = json.loads(event)
                        logger.debug(f'event: {event_dict["u"]}')
                        cache.update(event_dict)
                    except:
                        pass

                    if hasattr(self, 'on_depth_event'):
                        logger.debug('on_depth_event')
                        await self.on_depth_event(event_dict)

        async def _get_initial_depth_info():
            logger = self._logger('_get_initial_depth_info')

            depth = await self.get_depth_async(symbol)
            cache.set_initial_data(depth)
            logger.debug('depth ready')

            if hasattr(self, 'on_depth_ready'):
                logger.debug('on_depth_ready')
                await self.on_depth_ready()

        self._loop.run_until_complete(asyncio.gather(
            _watch_for_depth_events(),
            _get_initial_depth_info()
            ))

    def get_account_info(self):
        self._logger().info('get_account_info')
        return self._make_request(Endpoints.ACCOUNT_INFO, signed=True)

    def get_trade_info(self, symbol):
        self._logger('get_trade_info').info(symbol)
        return self._make_request(Endpoints.TRADE_INFO, signed=True,
                params={'symbol' : symbol})

    def get_open_orders(self, symbol):
        self._logger('get_open_orders').info(symbol)
        return self._make_request(Endpoints.OPEN_ORDERS, signed=True,
                params={'symbol' : symbol})

    def get_all_orders(self, symbol):
        self._logger('get_all_orders').info(symbol)
        return self._make_request(Endpoints.ALL_ORDERS, signed=True,
                params={'symbol' : symbol})

    def get_order_status(self, symbol, order_id):
        self._logger('get_order_status').info(f'{symbol}: {order_id}')
        return self._make_request(Endpoints.ORDER, signed=True,
                params={'symbol' : symbol, 'orderId' : order_id})

    def cancel_order(self, symbol, order_id):
        self._logger('cancel_order').info(f'{symbol}: {order_id}')
        return self._make_request(Endpoints.ORDER, verb='delete', signed=True,
                params={'symbol' : symbol, 'orderId' : order_id})

    def place_market_buy(self, symbol, quantity, **kwargs):
        self._logger('place_market_buy').info(f'{symbol}: {quantity}')

        params = {
            'symbol' : symbol,
            'side' : Sides.BUY,
            'type' : OrderTypes.MARKET,
            'quantity' : quantity,
            'recvWindow' : 60000
        }
        return self._make_request(Endpoints.ORDER, verb='post',
            signed=True, params=params)


    def place_market_sell(self, symbol, quantity, **kwargs):
        self._logger('place_market_sell').info(f'{symbol}: {quantity}')

        params = {
            'symbol' : symbol,
            'side' : Sides.SELL,
            'type' : OrderTypes.MARKET,
            'quantity' : quantity,
            'recvWindow' : 60000
        }
        return self._make_request(Endpoints.ORDER, verb='post',
                signed=True, params=params)


    def place_limit_buy(self, symbol, quantity, price, **kwargs):
        self._logger('place_limit_buy').info(f'{symbol}: {quantity} @ {price}')

        params = {
            'symbol' : symbol,
            'side' : Sides.BUY,
            'type' : OrderTypes.LIMIT,
            'timeInForce' : kwargs.get('time_in_force', TimeInForce.GTC),
            'quantity' : quantity,
            'price' : price,
            'recvWindow' : 60000
        }
        if 'stop_price' in kwargs:
            params['stopPrice'] = kwargs['stop_price']

        return self._make_request(Endpoints.ORDER, verb='post',
                signed=True, params=params)


    def place_limit_sell(self, symbol, quantity, price, **kwargs):
        self._logger('place_limit_sell').info(f'{symbol}: {quantity} @ {price}')

        params = {
            'symbol' : symbol,
            'side' : Sides.SELL,
            'type' : OrderTypes.LIMIT,
            'timeInForce' : kwargs.get('time_in_force', TimeInForce.GTC),
            'quantity' : quantity,
            'price' : price,
            'recvWindow' : 60000
        }
        if 'stop_price' in kwargs:
            params['stopPrice'] = kwargs['stop_price']

        return self._make_request(Endpoints.ORDER, verb='post',
                signed=True, params=params)


    def event(self, coro):
        """ Register a callback function on an event.

        Supported events:
          client.on_depth_ready
            fires when the initial /depth api call returns.

          client.on_depth_event
            fires whenever a @depth websocket event is received.
        """

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('event registered must be a cororoutine function')

        setattr(self, coro.__name__, coro)
