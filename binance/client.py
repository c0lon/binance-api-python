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


class BinanceClient(GetLoggerMixin):
    __loggername__ = 'BinanceClient'

    def __init__(self, apikey, apisecret):
        self.apikey = apikey
        self.apisecret = apisecret

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
        logger.info(f'{verb} {url}')

        response = getattr(requests, verb)(url, headers={
            'X-MBX-APIKEY' : self.apikey
        })
        response_json = response.json()

        if response.ok:
            return response.json()
        
        # don't overwrite 'msg' in log record
        response_json['error'] = response_json.pop('msg')
        logger.error(f'error: {response.reason}', exc_info=True)
        logger.debug(response_json['error'], extra=response_json)

        #import pdb; pdb.set_trace()
        raise response.raise_for_status()

    async def _make_request_async(self, path, verb='get', params=None, signed=False):
        logger = self._logger('_make_request_async')

        verb = verb.lower()
        url = self._prepare_request(path, verb, params, signed)
        logger.info(f'{verb} {url}')

        async with aiohttp.ClientSession() as client:
            response = await getattr(client, verb)(url, headers={
                'X-MBX-APIKEY' : self.apikey
            })

            response_json = await response.json(content_type=None)
            if response.reason == 'OK':
                logger.debug('success', extra=response_json)
                return response_json

            # don't overwrite 'msg' in log record
            response_json['error'] = response_json.pop('msg')
            logger.error(f'error: {response.reason}', exc_info=True)
            logger.debug(response_json['error'], extra=response_json)

            #import pdb; pdb.set_trace()
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
        params['recvWindow'] = 6000
        query_string = self._get_sorted_query_string(params)

        signature = hmac.new(
                self.apisecret.encode(),
                digestmod=hashlib.sha256)
        signature.update(query_string.encode())
    
        return '{}?{}&signature={}'.format(
                url, query_string, signature.hexdigest())

    def get_ticker(self, symbol=''):
        ticker = self._make_request('ticker/allPrices')

        if symbol:
            for _symbol in ticker:
                if _symbol['symbol'] == symbol:
                    return _symbol
            else:
                raise ValueError('invalid symbol: {}'.format(symbol))

        return ticker

    def get_depth(self, symbol):
        return self._make_request('depth', params={'symbol' : symbol})

    async def get_depth_async(self, symbol):
        return await self._make_request_async('depth',
                params={'symbol': symbol})

    def get_account_info(self):
        return self._make_request('account', signed=True)

    def get_open_orders(self, symbol):
        return self._make_request('openOrders', signed=True,
                params={'symbol' : symbol})

    def watch_depth(self, symbol):
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

    def event(self, coro):
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('event registered must be a cororoutine function')

        setattr(self, coro.__name__, coro)
