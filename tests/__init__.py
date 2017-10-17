import math
import os
import random
import shutil
import string

import yaml

import binance
from binance.utils import *


here = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(here, 'test')

root = os.path.dirname(here)
config_uri = os.path.join(root, 'development.yaml')
SETTINGS, GLOBAL_CONFIG = binance.configure_app(config_uri=config_uri)

APIKEY = SETTINGS['key']
APISECRET = SETTINGS['secret']


def random_boolean():
    return random.choice([True, False])


def random_string(min_length=8, max_length=16, cant_be=None):
    length = random.randint(min_length, max_length)
    s = ''.join([random.choice(string.hexdigits) for _ in range(length)])
    while s == cant_be:
        s = ''.join([random.choice(string.hexdigits) for _ in range(length)])
    return s


def random_number(min_=0, max_=1000000000, type_=int, cant_be=None):
    n = min_ + random.random() * (max_ - min_)
    while type(n) == cant_be:
        n = min_ + random.random() * (max_ - min_)
    return type_(n)


def random_dir():
    depth = random.randint(1, 3)
    return os.path.join(TEST_DIR, *[random_string() for _ in range(depth)])


def randomly_populate_file(filepath):
    file_size = random.randint(1024, 70656)
    file_contents = os.urandom(file_size)
    with open(filepath, 'wb+') as f:
        f.write(file_contents)

    return file_contents


def randomly_populate_dir(directory):
    file_count = random.randint(4, 32)
    files = {}
    for _ in range(file_count):
        filepath = os.path.join(directory, '{}.dat'.format(random_string()))
        files[filepath] = randomly_populate_file(filepath)

    return files
