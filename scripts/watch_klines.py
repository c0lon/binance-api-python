""" Watch the klines of a given symbol.
"""


import signal
import sys

from binance import (
    BinanceClient,
    configure_app,
    get_default_arg_parser,
    )


def quit_handler(signum, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, quit_handler)
signal.signal(signal.SIGTERM, quit_handler)


def main():
    arg_parser = get_default_arg_parser()
    arg_parser.add_argument('symbol', type=str,
            help='watch the klines of symbol <SYMBOL>.')
    arg_parser.add_argument('interval', type=str,
            help='set the klines interval.')
    arg_parser.add_argument('-d', '--depth', type=int,
            help='display the <DEPTH> latest klines.')

    settings, config = configure_app(arg_parser=arg_parser)
    symbol = config['args']['symbol']
    interval = config['args']['interval']
    depth = config['args']['depth']

    client = BinanceClient(settings['apikey'], settings['apisecret'])

    @client.event
    async def on_klines_ready():
        """ This coroutine runs when the inital /klines API call returns.
        """
        print('klines ready')
        client.klines_cache[(symbol, interval)].pretty_print(depth)
    
    @client.event
    async def on_klines_event(event):
        """ This coroutine runs whenever a @klines websocket event is received.
        """
        client.klines_cache[(symbol, interval)].pretty_print(depth)

    client.watch_klines(symbol, interval)


if __name__ == '__main__':
    main()
