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
    arg_parser.add_argument('-l', '--depth-limit', type=int,
            help='show the <DEPTH> latest orders on each side.')

    settings, config = configure_app(arg_parser=arg_parser)
    symbol = config['args']['symbol']
    depth_limit = config['args']['depth_limit']

    client = BinanceClient(settings['apikey'], settings['apisecret'])

    @client.event
    async def on_depth_ready(depth):
        """ This coroutine runs when the inital /depth API call returns.
        """
        print('depth ready')
        client.depth_cache[symbol].pretty_print(depth_limit)
    
    @client.event
    async def on_depth_event(event):
        """ This coroutine runs whenever a @depth websocket event is received.
        """
        print(f'update id: {event["u"]}') # print the event id
        client.depth_cache[symbol].pretty_print(depth_limit)

    client.watch_depth(symbol)


if __name__ == '__main__':
    main()
