""" Watch the candlesticks of a given symbol.
"""


from datetime import datetime
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
            help='watch the candlesticks of symbol <SYMBOL>.')
    arg_parser.add_argument('interval', type=str,
            help='set the candlesticks interval.')
    arg_parser.add_argument('-d', '--depth', type=int,
            help='display the <DEPTH> latest candlesticks.')

    settings, config = configure_app(arg_parser=arg_parser)
    symbol = config['args']['symbol']
    interval = config['args']['interval']
    depth = config['args']['depth']

    client = BinanceClient(settings['apikey'], settings['apisecret'])

    @client.event
    async def on_candlesticks_ready():
        """ This coroutine runs when the inital /candlesticks API call returns.
        """
        print('candlesticks ready')
        client.candlestick_cache[(symbol, interval)].pretty_print(depth)
    
    @client.event
    async def on_candlesticks_event(event):
        """ This coroutine runs whenever a @candlesticks websocket event is received.
        """
        cache = client.candlestick_cache[(symbol, interval)]
        latest_candlestick = cache.candlesticks[-1]
        date_string = latest_candlestick.open_time.strftime('%Y-%m-%d %H:%M:%S')
        event_date_string = datetime.fromtimestamp(event['E'] / 1000)
        print(f'UPDATE {event_date_string}\n')
        print(f'{latest_candlestick.symbol} {date_string}')
        print(f'      open: {latest_candlestick.price.open}')
        print(f'      high: {latest_candlestick.price.high}')
        print(f'       low: {latest_candlestick.price.low}')
        print(f'     close: {latest_candlestick.price.low}')
        print(f'    volume: {latest_candlestick.volume}')
        print()

    client.watch_candlesticks(symbol, interval)


if __name__ == '__main__':
    main()
