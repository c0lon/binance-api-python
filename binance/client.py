""" Binance API Client.
"""


import asyncio
import hashlib
import hmac
import json
import time
from urllib.parse import quote

import aiohttp
import requests
import websockets as ws

from .cache import (
    DepthCache,
    CandlestickCache,
    )
from .enums import (
    OrderSides,
    OrderTypes,
    TimeInForce,
    )
from .storage import (
    Account,
    Candlestick,
    Deposit,
    Depth,
    Order,
    Ticker,
    Trade,
    Withdraw,
    )
from .utils import GetLoggerMixin


API_BASE_URL = 'https://www.binance.com'

WEBSOCKET_BASE_URL = 'wss://stream.binance.com:9443/ws/{symbol}'
DEPTH_WEBSOCKET_URL = '{}@depth'.format(WEBSOCKET_BASE_URL)
KLINE_WEBSOCKET_URL = '{}@kline'.format(WEBSOCKET_BASE_URL)

CONTENT_TYPE = 'x-www-form-urlencoded'


class Endpoints:
    PING = 'api/v1/ping'
    SERVER_TIME = 'api/v1/time'
    ACCOUNT_INFO = 'api/v3/account'
    TRADE_INFO = 'api/v3/myTrades'
    ORDER = 'api/v3/order'
    ALL_ORDERS = 'api/v3/allOrders'
    OPEN_ORDERS = 'api/v3/openOrders'
    TICKER_ALL = 'api/v1/ticker/allPrices'
    TICKER_BEST = '/api/v1/ticker/allBookTickers'
    TICKER_24HR = '/api/v1/ticker/ticker/24hr'
    DEPTH = 'api/v1/depth'
    KLINES = 'api/v1/klines'
    WITHDRAW = 'wapi/v1/withdraw.html'
    WITHDRAW_HISTORY = 'wapi/v1/getWithdrawHistory.html'
    DEPOSIT_HISTORY = 'wapi/v1/getDepositHistory.html'


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
        self.candlestick_cache = {}

    def _prepare_request(self, path, verb, params, signed):
        params = params or {}

        if signed:
            url = self._sign_request(path, params)
        elif params:
            query_string = self._get_sorted_query_string(params)
            url = '{}/{}?{}'.format(API_BASE_URL, path, query_string)
        else:
            url = '{}/{}'.format(API_BASE_URL, path)

        return url

    def _make_request(self, path, verb='get', params=None, signed=False):
        logger = self._logger('_make_request')

        verb = verb.lower()
        url = self._prepare_request(path, verb, params, signed)
        logger.info(f'{verb.upper()} {url}')

        http_function = getattr(requests, verb)
        response = http_function(url, headers=self.headers)
        response_json = response.json()

        # don't overwrite 'msg' in log record
        if 'msg' in response_json:
            response_json['message'] = response_json.pop('msg')

        if response.ok:
            return response.json()

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

            # don't overwrite 'msg' in log record
            if 'msg' in response_json:
                response_json['message'] = response_json.pop('msg')

            if response.reason == 'OK':
                logger.debug('success', extra={'response' : response_json})
                return response_json

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
        url = '{}/{}'.format(API_BASE_URL, path)

        params['timestamp'] = int(round(time.time() * 1000.0))
        if 'recvWindow' not in params: params['recvWindow'] = 6000
        query_string = self._get_sorted_query_string(params)

        signature = hmac.new(
                self.apisecret.encode(),
                digestmod=hashlib.sha256)
        signature.update(query_string.encode())

        return '{}?{}&signature={}'.format(
                url, query_string, signature.hexdigest())

    def ping(self):
        self._make_request(Endpoints.PING)
        return True

    def get_server_time(self):
        server_time = self._make_request(Endpoints.SERVER_TIME)
        return server_time['serverTime']

    def get_ticker(self, symbol=''):
        self._logger('get_ticker').info(symbol)
        raw_tickers = self._make_request(Endpoints.TICKER_ALL)

        if symbol:
            for raw_ticker in raw_tickers:
                if raw_ticker['symbol'] == symbol:
                    return Ticker(raw_ticker)
            else:
                raise ValueError(f'invalid symbol: {symbol}')
        else:
            return [Ticker(rt) for rt in raw_tickers]

    def get_depth(self, symbol):
        self._logger('get_depth').info(symbol)
        depth = self._make_request(Endpoints.DEPTH, params={'symbol' : symbol})

        return Depth(symbol, depth)

    async def get_depth_async(self, symbol, **kwargs):
        self._logger('get_depth_async').info(symbol)
        raw_depth = await self._make_request_async(Endpoints.DEPTH,
                params={'symbol': symbol})

        depth = Depth(symbol, raw_depth)
        await self._handle_callback(kwargs.get('callback'), depth)

        return depth

    def watch_depth(self, symbol):
        self._logger('watch_depth').info(symbol)

        cache = self.depth_cache.get(symbol)
        if not cache:
            cache = DepthCache()
            self.depth_cache[symbol] = cache

        async def _watch_for_depth_events():
            logger = self._logger('_watch_for_depth_events')

            url = DEPTH_WEBSOCKET_URL.format(symbol=symbol.lower())
            logger.debug(f'opening websocket connection: {url}')
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
                await self.on_depth_ready(depth)

        self._loop.run_until_complete(asyncio.gather(
            _watch_for_depth_events(),
            _get_initial_depth_info()
        ))

    def get_candlesticks(self, symbol, interval, **kwargs):
        self._logger('get_candlesticks').info(f'{symbol} {interval}')

        params = {
            'symbol' : symbol,
            'interval' : interval,
            'limit' : kwargs.get('limit', 500)
        }
        if 'start_time' in kwargs:
            params['startTime'] = kwargs['start_time']
        if 'end_time' in kwargs:
            params['endTime'] = kwargs['end_time']

        raw_candlesticks = self._make_request(Endpoints.KLINES,
                verb='get', params=params)
        return [Candlestick(symbol, cs) for cs in raw_candlesticks]

    async def get_candlesticks_async(self, symbol, interval, **kwargs):
        logger = self._logger('get_candlesticks_async')
        logger.info(f'{symbol} {interval}')

        params = {
            'symbol' : symbol,
            'interval' : interval,
            'limit' : kwargs.get('limit', 500)
        }
        if 'start_time' in kwargs:
            params['startTime'] = kwargs['start_time']
        if 'end_time' in kwargs:
            params['endTime'] = kwargs['end_time']

        raw_candlesticks = await self._make_request_async(Endpoints.KLINES,
                verb='get', params=params)
        candlesticks = [Candlestick(symbol, cs) for cs in raw_candlesticks]
        await self._handle_callback(kwargs.get('callback'), candlesticks)

        return candlesticks
        
    async def _handle_callback(self, callback, *values):
        if not callback:
            return

        if asyncio.iscoroutinefunction(callback):
            await callback(*values)
        elif hasattr(callback, '__call__'):
            callback(*values)
        else:
            logger.error(f'callback function {callback.__name__} must be a function or a coroutine, not "{type(callback).__name__}"')

    def watch_candlesticks(self, symbol, interval, **kwargs):
        self._logger('watch_candlesticks').info(f'{symbol} {interval}')

        cache = self.candlestick_cache.get((symbol, interval))
        if not cache:
            cache = CandlestickCache()
            self.candlestick_cache[(symbol, interval)] = cache

        async def _watch_for_candlesticks_events():
            logger = self._logger('_watch_for_candlestick_events')

            url = KLINE_WEBSOCKET_URL.format(symbol=symbol.lower())
            url += '_{}'.format(interval)
            logger.debug(f'opening websocket connection: {url}')
            async with ws.connect(url) as socket:
                while True:
                    event = await socket.recv()
                    try:
                        event_dict = json.loads(event)
                        logger.debug(f'event: {event_dict["E"]}')
                        cache.update(event_dict)
                    except:
                        pass

                    if hasattr(self, 'on_candlesticks_event'):
                        logger.debug('on_candlesticks_event')
                        await self.on_candlesticks_event(event_dict)

        async def _get_initial_candlesticks_info():
            logger = self._logger('_get_initial_candlesticks_info')

            candlesticks = await self.get_candlesticks_async(symbol, interval)
            cache.set_initial_data(candlesticks)
            logger.debug('candlesticks ready')

            if hasattr(self, 'on_candlesticks_ready'):
                logger.debug('on_candlesticks_ready')
                await self.on_candlesticks_ready()

        self._loop.run_until_complete(asyncio.gather(
            _watch_for_candlesticks_events(),
            _get_initial_candlesticks_info()
        ))

    def get_account_info(self):
        self._logger().info('get_account_info')
        raw_account = self._make_request(Endpoints.ACCOUNT_INFO, signed=True)
        return Account(raw_account)

    def get_trade_info(self, symbol):
        self._logger('get_trade_info').info(symbol)
        raw_trades = self._make_request(Endpoints.TRADE_INFO,
                signed=True, params={'symbol' : symbol})

        return [Trade(symbol, t) for t in raw_trades]

    def get_open_orders(self, symbol):
        self._logger('get_open_orders').info(symbol)
        raw_orders = self._make_request(Endpoints.OPEN_ORDERS,
                signed=True, params={'symbol' : symbol})

        return [Order(o) for o in raw_orders]

    def get_all_orders(self, symbol):
        self._logger('get_all_orders').info(symbol)
        raw_orders = self._make_request(Endpoints.ALL_ORDERS,
                signed=True, params={'symbol' : symbol})

        return [Order(o) for o in raw_orders]

    def get_order_status(self, symbol, order_id):
        self._logger('get_order_status').info(f'{symbol}: {order_id}')
        raw_order = self._make_request(Endpoints.ORDER, signed=True,
                params={'symbol' : symbol, 'orderId' : order_id})
        
        return Order(raw_order)

    def cancel_order(self, symbol, order_id):
        self._logger('cancel_order').info(f'{symbol}: {order_id}')
        raw_order = self._make_request(Endpoints.ORDER, verb='delete', signed=True,
                params={'symbol' : symbol, 'orderId' : order_id})

        return True

    def place_market_buy(self, symbol, quantity, **kwargs):
        self._logger('place_market_buy').info(f'{symbol}: {quantity}')

        params = {
            'symbol' : symbol,
            'side' : OrderSides.BUY,
            'type' : OrderTypes.MARKET,
            'quantity' : quantity,
            'recvWindow' : 60000
        }
        raw_order = self._make_request(Endpoints.ORDER,
                verb='post', signed=True, params=params)

        return Order(raw_order)

    def place_market_sell(self, symbol, quantity, **kwargs):
        self._logger('place_market_sell').info(f'{symbol}: {quantity}')

        params = {
            'symbol' : symbol,
            'side' : OrderSides.SELL,
            'type' : OrderTypes.MARKET,
            'quantity' : quantity,
            'recvWindow' : 60000
        }
        raw_order = self._make_request(Endpoints.ORDER,
                verb='post', signed=True, params=params)

        return Order(raw_order)

    def place_limit_buy(self, symbol, quantity, price, **kwargs):
        self._logger('place_limit_buy').info(f'{symbol}: {quantity} @ {price}')

        params = {
            'symbol' : symbol,
            'side' : OrderSides.BUY,
            'type' : OrderTypes.LIMIT,
            'timeInForce' : kwargs.get('time_in_force', TimeInForce.GTC),
            'quantity' : quantity,
            'price' : price,
            'recvWindow' : 60000
        }
        if 'stop_price' in kwargs:
            params['stopPrice'] = kwargs['stop_price']

        raw_order = self._make_request(Endpoints.ORDER,
                verb='post', signed=True, params=params)

        return Order(raw_order)

    def place_limit_sell(self, symbol, quantity, price, **kwargs):
        self._logger('place_limit_sell').info(f'{symbol}: {quantity} @ {price}')

        params = {
            'symbol' : symbol,
            'side' : OrderSides.SELL,
            'type' : OrderTypes.LIMIT,
            'timeInForce' : kwargs.get('time_in_force', TimeInForce.GTC),
            'quantity' : quantity,
            'price' : price,
            'recvWindow' : 60000
        }
        if 'stop_price' in kwargs:
            params['stopPrice'] = kwargs['stop_price']

        raw_order = self._make_request(Endpoints.ORDER,
                verb='post', signed=True, params=params)

        return Order(raw_order)

    def withdraw(self, asset, amount, address, **kwargs):
        logger = self._logger('withdraw')
        logger.info(f'{amount} {asset} -> {address}')

        params = {
            'asset' : asset,
            'amount' : amount,
            'address' : address
        }
        response = self._make_request(Endpoints.WITHDRAW,
                verb='post', signed=True, params=params)
        if not response.get('success'):
            logger.error('failed request', extra=response)
            return

        return response['success']

    def get_withdraw_history(self, asset='', **kwargs):
        logger = self._logger('get_withdraw_history')

        params = {}
        if asset:
            logger.info(asset)
            params['asset'] = asset

        response = self._make_request(Endpoints.WITHDRAW_HISTORY,
                verb='post', signed=True, params=params)
        if not response.get('success'):
            logger.error('failed request', extra=response)
            return

        return [Withdraw(withdraw) for withdraw in response['withdrawList']]

    def get_deposit_history(self, asset='', **kwargs):
        logger = self._logger('get_deposit_history')

        params = {}
        if asset:
            logger.info(asset)
            params['asset'] = asset

        response = self._make_request(Endpoints.DEPOSIT_HISTORY,
                verb='post', signed=True, params=params)
        if not response.get('success'):
            logger.error('failed request', extra=response)
            return

        """ TODO
        wait for API fix that enforces the `asset` parameter.
        Currently it does not, so filter out deposits after
        the API call returns.
        """
        deposits = []
        if asset:
            for deposit in response['depositList']:
                if deposit['asset'] == asset:
                    deposits.append(deposit)
        else:
            deposits = response['depositList']

        return [Deposit(d) for d in deposits]

    def event(self, coro):
        """ Register a callback function on an event.

        Supported events:
          client.on_depth_ready
            fires when the initial /depth api call returns.

          client.on_depth_event
            fires whenever a @depth websocket event is received.

          client.on_candlesticks_ready
            fires when the initial /klines api call returns

          client.on_candlesticks_event
            fires whenever a @klines websocket event is received
        """

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('event registered must be a cororoutine function')

        setattr(self, coro.__name__, coro)
