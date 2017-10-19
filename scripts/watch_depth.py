""" Watch the depth of a given symbol.
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
            help='watch the depth of symbol <SYMBOL>.')

    settings, config = configure_app(arg_parser=arg_parser)
    symbol = config['args']['symbol']

    client = BinanceClient(settings['apikey'], settings['apisecret'])

    @client.event
    async def on_depth_ready():
        """ This coroutine runs when the inital /depth API call returns.
        """
        print('depth ready')
        client.depth_cache[symbol].pretty_print()
    
    @client.event
    async def on_depth_event(event):
        """ This coroutine runs whenever a @depth websocket event is received.
        """
        print(f'id: {event["u"]}') # print the event id
        client.depth_cache[symbol].pretty_print()

    client.watch_depth(symbol)


if __name__ == '__main__':
    main()
