# binance

Python client for the [Binance API](https://www.binance.com/restapipub.html).

Requires python 3.5 or greater.

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

See the [pytest docs](https://docs.pytest.org/en/latest/contents.html)
for more information.

### Enabling all tests

By default, tests for functions which aim to change the state
of your account are disabled. To enable them, edit
[pytest.ini](pytest.ini) by changing

```
[pytest]
testpaths = tests/test_fetchers.py
```

to

```
[pytest]
testpaths = tests
```

then follow the instructions in (tests/test_actions.py)[tests/test_actions.py].

### WARNING

Enabling these tests means that your account balances will be changed
if the tests are successful. Follow the configuration instructions
**very carefully.** Failing to do so could result in the tests altering
your account in a negative way.

## Usage

```python
from binance import BinanceClient

client = BinanceClient(apikey, apisecret)
client.ping()
```

### Client Methods

Methods with names ending with `_async` are asynchronous `coroutines`
that perform the same action as their synchronous counterpart.
(Read more about Python's asynchronous features
[here](https://docs.python.org/3/library/asyncio.html).)

#### Public Endpoints

##### `/ping`

```
def ping()
```

##### `/time`
```
def get_server_time()
```

##### `/ticker`
```
def get_ticker(self, symbol='')
```

##### `/depth`
```
def get_depth(self, symbol)
```
```
async def get_depth_async(self, symbol)
```

##### `/klines`
```
def get_candlesticks(self, symbol, interval, **kwargs)
```
```
async def get_candlesticks_async(self, symbol, interval, **kwargs)
```

#### Signed Endpoints

#### Websocket Endpoints

### Scripts

In order for the scripts below to work correctly, you must put your
`apiKey` and `secretKey` into the `apikey` and `apisecret` slots
in [config.yaml](config.yaml), respectively.

### watchdepth

See [watch_depth.py](scripts/watch_depth.py) for an example of how to
use the asynchronous `watch_depth()` method.

`watchdepth config.ini <SYMBOL>`

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


### watchcandlesticks

See [watch_candlesticks.py](scripts/watch_candlesticks.py) for an example of how to
use the asynchronous `watch_candlesticks()` method.

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
