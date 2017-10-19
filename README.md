# binance

## Goals

Build API clients with the following features:
- [x] Follow latest api documentation
- [x] Getting latest price of a symbol
- [x] Getting depth of a symbol or maintain a depth cache locally
- [x] Placing a LIMIT order
- [x] Placing a MARKET order
- [x] Checking an order’s status
- [x] Cancelling an order
- [x] Getting list of open orders
- [x] Getting list of current position

## Usage

`python setup.py install`

```python
from binance import BinanceClient

client = BinanceClient(apikey, apisecret)
client.get_account_info()
```

See [watch_depth.py](scripts/watch_depth.py) for an example of how to
use the asynchronous `watch_depth()` method. In order for the script
to work correctly, you must put your `apiKey` and `secretKey` into
the `apikey` and `apisecret` slots in [config.yaml][config.yaml], respectively.

```
usage: watchdepth [-h] [--log-level {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                  [--version] [--debug]
                  config_uri symbol

positional arguments:
  config_uri            the config file to use.
  symbol                watch the depth of symbol <SYMBOL>.

optional arguments:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARN,ERROR,CRITICAL}
  --version             Show the package version and exit.
  --debug
```
