from urllib.parse import urljoin

import requests

from .utils import (
    GetLoggerMixin,
    )


API_BASE_URL = 'https://www.binance.com/api/v1/'


class BinanceClient(GetLoggerMixin):
    BASE_URL = ''

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self._session = requests.Session()

    def get_ticker(self, symbol=''):
        response = self._make_request('ticker/allPrices')
        ticker = {}
        for symbol_ in response:
            ticker[symbol_['symbol']] = float(symbol_['price'])

        if symbol:
            if symbol not in ticker:
                raise ValueError('invalid symbol: {}'.format(symbol))
            return ticker[symbol]

        return ticker

    def _make_request(self, path, verb='GET', signed=False):
        request = requests.Request(verb, urljoin(API_BASE_URL, path))

        if signed:
            self._sign_request(request)

        prepared_request = request.prepare()
        response = self._session.send(prepared_request)
        if response.ok:
            return response.json()

    def _sign_request(self, request):
        pass
