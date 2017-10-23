# binance

Python client for the
[Binance API](https://www.binance.com/restapipub.html).

Requires python 3.6 or greater.

## Installation

```
git clone https://github.com/c0lon/binance.git
cd binance
python setup.py install
```

## Tests

First, enter your API key and secret into
[tests/config.yaml](tests/config.yaml).
Then run the command below:

`python setup.py test`

Any log messages are written to `tests/test.log`.

To enter a `pdb` shell on a test failure, run

`pytest --pdb`

See the
[pytest docs](https://docs.pytest.org/en/latest/contents.html)
for more information.

### Enabling all tests

By default, tests that would change your account in any way,
such as placing an order or withdrawing funds, are disabled.
To enable them, edit [pytest.ini](pytest.ini) by changing

```
[pytest]
testpaths = tests/test_fetchers.py
```

to

```
[pytest]
testpaths = tests
```

then follow the instructions in
[tests/test_actions.py](tests/test_actions.py).

#### WARNING

Enabling these tests means that your account balances will be
changed if the tests are successful. Follow the configuration
instructions **very carefully.** Failing to do so could result
in the tests altering your account in a negative way.

## Usage

```python
from binance import BinanceClient

client = BinanceClient(apikey, apisecret)
client.ping()
```


### Storage Classes

Most client methods described below return objects that can be found
in [binance/storage.py](binance/storage.py). These objects convert
values into their natives types, including:
* decimal strings to `float`
* timestamps to `datetime.datetime`

Each object accepts a raw API version of the object in its constructor.
These objects also have a `to_json()` method that returns the object
as a JSON-dumpable dictionary.


### Client Methods

Methods with names ending with `_async` are asynchronous `coroutines`
that perform the same action as their synchronous counterpart.
(Read more about Python's asynchronous features
[here](https://docs.python.org/3/library/asyncio.html).)

#### Public Endpoint Methods

##### `/ping`

```
def ping()
```

##### `/time`
```
def get_server_time()
```
Return the server time in milliseconds as an integer.

##### `/ticker`
Return `binance.storage.Ticker`.
```
def get_ticker(self, symbol='')
```

##### `/depth`
Return `binance.storage.Depth`.
```
def get_depth(self, symbol)
async def get_depth_async(self, symbol)
```

##### `/klines`
Return list of `binance.storage.Candlestick`.
```
def get_candlesticks(self, symbol, interval, **kwargs)
async def get_candlesticks_async(self, symbol, interval, **kwargs)
```

#### Signed Endpoint Methods

##### `/myTrades`
Return list of `binance.storage.Trade`.
```
def get_trade_info(self, symbol)
```

##### `/openOrders`
Return list of `binance.storage.Order`.
```
def get_open_orders(self, symbol)
```

##### `/allOrders`
Return list of `binance.storage.Order`.
```
def get_all_orders(self, symbol):
```

##### `/order`
Return raw API `/order` JSON response.
```
def get_order_status(self, symbol, order_id)
def place_market_buy(self, symbol, quantity, **kwargs)
def place_market_sell(self, symbol, quantity, **kwargs)
def place_limit_buy(self, symbol, quantity, price, **kwargs)
def place_limit_sell(self, symbol, quantity, price, **kwargs)
```

##### `/withdraw`
Return `True` if the withdraw is successfully initiated.
```
def withdraw(self, asset, amount, address, **kwargs)
```

##### `/withdrawHistory.html`
Return list of `binance.storage.Withdraw`.
```
def get_withdraw_history(self, asset='', **kwargs)
```

##### `/depositHistory.html`
Return list of `binance.storage.Deposit`.
```
def get_deposit_history(self, asset='', **kwargs)
```

#### Websocket Endpoint Methods

##### `@depth`
```
def watch_depth(self, symbol)
```
See [watch_depth.py](scripts/watch_depth.py) for an example of how to
use the asynchronous `watch_depth()` method.

##### `@kline`
```
def watch_candlesticks(self, symbol)
```
See [watch_candlesticks.py](scripts/watch_candlesticks.py) for an
example of how to use the asynchronous `watch_candlesticks()` method.  

#### Event Callback Methods
```
def event(self, coro)
```
Register an asynchronous `coroutine` that is fired on certain client
events.

Supported Events:
* `on_depth_ready`
* `on_depth_event`
* `on_candlesticks_ready`
* `on_candlesticks_event`

See [scripts/watch_depth.py](scripts/watch_depth.py) and
[scripts/watch_candlesticks.py](scripts/watch_candlesticks.py)
for examples.


### Scripts

In order for the scripts below to work correctly, you must put your
`apiKey` and `secretKey` into the `apikey` and `apisecret` slots
in [config.yaml](config.yaml), respectively.

#### [watchdepth](scripts/watch_depth.py)
```
usage: watchdepth [-h] [--log-level {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                  [--version] [--debug] [-l DEPTH_LIMIT]
                  config_uri symbol

positional arguments:
  config_uri            the config file to use.
  symbol                watch the depth of symbol <SYMBOL>.

optional arguments:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARN,ERROR,CRITICAL}
  --version             Show the package version and exit.
  --debug
  -l DEPTH_LIMIT, --depth-limit DEPTH_LIMIT
                        show the <DEPTH> latest orders on each side.
```

#### [watchcandlesticks](scripts/watch_candlesticks.py)
```
usage: watchcandlesticks [-h] [--log-level {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                         [--version] [--debug] [-d DEPTH]
                         config_uri symbol interval

positional arguments:
  config_uri            the config file to use.
  symbol                watch the candlesticks of symbol <SYMBOL>.
  interval              set the candlesticks interval.

optional arguments:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARN,ERROR,CRITICAL}
  --version             Show the package version and exit.
  --debug
  -d DEPTH, --depth DEPTH
                        display the <DEPTH> latest candlesticks.
```
