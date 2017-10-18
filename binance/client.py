import hashlib
import hmac
import time
from urllib.parse import (
    quote,
    urljoin,
    )

import aiohttp
import requests
import websockets

from .utils import GetLoggerMixin


API_BASE_URL = 'https://www.binance.com/api/'


class BinanceClient(GetLoggerMixin):

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def _prepare_request(self, path, verb, params, signed):
        params = params or {}

        if signed:
            url = self._sign_request(path, params)
        elif params:
            url = '{}/v1/{}?{}'.format(API_BASE_URL, path, self._get_sorted_query_string(params))
        else:
            url = '{}/v1/{}'.format(API_BASE_URL, path)

        return url

    def _make_request(self, path, verb='get', params=None, signed=False):
        verb = verb.lower()

        url = self._prepare_request(path, verb, params, signed)
        response = getattr(requests, verb)(url, headers={
            'X-MBX-APIKEY' : self.api_key
        })
        if response.ok:
            return response.json()
        
        raise response.raise_for_status()

    async def _make_request_async(self, path, verb='get', params=None, signed=False):
        verb = verb.lower()

        url = self._prepare_request(path, verb, params, signed)
        with aiohttp.ClientSession() as client:
            response = await getattr(client, verb)(url, headers={
                'X-MBX-APIKEY' : self.api_key
            })
            if response.reason == 'OK':
                return await response.json(content_type=None)

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
                self.api_secret.encode(),
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
        return await self._make_request_async('depth', params={'symbol': symbol})

    def get_account_info(self):
        return self._make_request('account', signed=True)
