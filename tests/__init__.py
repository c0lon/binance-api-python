import os

from binance import (
    BinanceClient,
    configure_app,
    )


TEST_CONFIG_FILE = 'config.yaml'

root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
config_uri = os.path.join(here, TEST_CONFIG_FILE)
SETTINGS, GLOBAL_CONFIG = configure_app(config_uri=config_uri)

APIKEY = SETTINGS['apikey']
APISECRET = SETTINGS['apisecret']
CLIENT = BinanceClient(APIKEY, APISECRET)

ASSETS = [
    'BTC',
    'ETH',
]
SYMBOLS = [
    'ETHBTC',
    'LTCBTC',
    'BNBBTC',
    'NEOBTC',
    'OMGBTC',
    'WTCBTC',
]
