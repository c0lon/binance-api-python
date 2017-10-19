import math
import os
import random
import shutil
import string

import yaml

import binance


here = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(here, 'test')

root = os.path.dirname(here)
config_uri = os.path.join(root, 'development.yaml')
SETTINGS, GLOBAL_CONFIG = binance.configure_app(config_uri=config_uri)

APIKEY = SETTINGS['apikey']
APISECRET = SETTINGS['apisecret']
