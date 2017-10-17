from argparse import ArgumentParser
import logging.config
import os
import sys

import yaml

from .binance import BinanceClient


here = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
with open(os.path.join(here, 'VERSION')) as f:
    __version__ = f.read().strip()
__author__ = 'c0lon'
__email__ = ''


def configure_app(config_uri='', arg_parser=None):
    ''' Configure the application.

    :param config_uri:
        If != '', app is configured using the file at the given
        path, if it exists. Else require a config_uri as a command
        line argument.
    :type config_uri: str
    :param arg_parser:
        If None, a minimal argument parser is created. A config uri
        is required and the log level can be optionally set.
    :type arg_parser: argparse.ArgumentParser

    :return:
        Return a tuple of the `main` section of the config and
        the entire config object.
    :rtype: ({}, {})
    '''

    args = {'config_uri' : config_uri}
    if not args['config_uri']:
        arg_parser = arg_parser or ArgumentParser()
        arg_parser.add_argument('config_uri', type=str,
                help='the config file to use.')
        arg_parser.add_argument('--log-level', type=str,
                choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'])
        arg_parser.add_argument('--version', action='store_true',
                help='Show the package version and exit.')
        arg_parser.add_argument('--debug', action='store_true')
        args = vars(arg_parser.parse_args())

    if args.pop('version', None):
        print(__version__)
        sys.exit(0)

    try:
        with open(args['config_uri']) as f:
            config = yaml.load(f)
    except:
        print('invalid config file: {}'.format(args['config_uri']))
        sys.exit(1)
    else:
        config['args'] = args

    if args.get('log_level'):
        config['logging']['root']['level'] = args.pop('log_level')
    logging.config.dictConfig(config['logging'])

    config['main'] = config.get('main', {})
    config['main']['debug'] = args.get('debug', False)

    return config['main'], config

