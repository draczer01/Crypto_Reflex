# Cryptocurrency Portfolio Balancer

**USE AT YOUR OWN RISK. THIS TRADES REAL MONEY. NO WARRANTY IS GIVEN**

A script that can connect to a cryptocurrency exchange and buy/sell cryptocurrency to keep your portfolio balancer to a certain ratio.
this fork supports the use of a proxy in case you need to use a static ip address.

This fork was made to be used on Xponential crypto: https://xcryptofund.io


## Install

Via Pip:
```
pip install crypto_reflex
```

Via source from Github:

```
git clone https://github.com/draczer01/Crypto_Reflex.git
cd crypto_reflex
virtualenv --python=python3 .
. bin/activate
pip install -r requirements.txt
pip install -e .
```

## Use the library in your projects

```
from crypto_reflex.crypto_reflex_lib import crypto_reflex_lib # import the ligrary
cryptoReflex = crypto_reflex_lib
rebalance = cryptoReflex("binance", "{\"XRP\": 40.0, \"XLM\": 20.0, \"BTC\": 10.0, \"ETH\": 10.0, \"BNB\": 10.0, \"USDT\": 10.0}", "API_KEY", "API_SECRET", 0.2)
print(rebalance) # prints the output in JSON
```
example of a return in JSON:

```
{"portfolio_value": 3.8687923544999996, "currency": "USDT", "cost": "0.002321"}
```
## error codes
while using the library on your project, you may encounter the following statuses:

0: no rebalancing needed  
1: rebalance successful  
2: target format is invalid  
3: incorrect target allocation  
4: could not find a better portfolio, please wait a while and retry  

example:

```
{"status": 1, "message": "Total target needs to equal 100, it is 98"}
```

## Config
THIS DOES NOT APPLY IF YOU ARE USING IT AS A LIBRARY  
Create a config file in `config.ini` with the definition of your exchange and portfolio percentages, and threshold (percent) that rebalancing is needed.
An example config file is included at `config.ini.example` but below is all you need:

```
[binance]
api_key = <api key>
api_secret = <api secret>
threshold = 2.0
targets = XRP 40
          BTC 20
	  ETH 20
	  BNB 10
	  USDT 10
```

By default it values the portfolio in USDT, this can be changed with `--valuebase` argument.

To configure a proxy, simply create an environment variable named `PROXY_URL`

To get the data returned as JSON simply use: `--json` 

## Running

Dry run (don't actually trade) against Binance
```
$ crypto_reflex binance
Connected to exchange: binance

Current Portfolio:
  XRP    3272.28  (39.92 / 40.00%)
  BTC    0.14     (20.05 / 20.00%)
  ETH    3.85     (20.02 / 20.00%)
  BNB    22.81    ( 9.99 / 10.00%)
  USDT   262.48   (10.02 / 10.00%)

  Total value: 2619.40 USDT
  Balance error: 0.043 / 0.08

No balancing needed
```

To force it to rebalance regardless of if needed:
```
$ crypto_reflex --force binance
Connected to exchange: binance

Current Portfolio:
  XRP    3272.28  (39.92 / 40.00%)
  BTC    0.14     (20.04 / 20.00%)
  ETH    3.85     (20.02 / 20.00%)
  BNB    22.81    ( 9.99 / 10.00%)
  USDT   262.48   (10.02 / 10.00%)

  Total value: 2619.28 USDT
  Balance error: 0.042 / 0.08

Balancing needed [FORCED]:

Proposed Portfolio:
  XRP    3278.51  (40.00 / 40.00%)
  BTC    0.14     (20.04 / 20.00%)
  ETH    3.83     (19.95 / 20.00%)
  BNB    22.81    ( 9.99 / 10.00%)
  USDT   262.48   (10.02 / 10.00%)

  Total value: 2619.28 USDT
  Balance error: 0.032definition
  Total fees to re-balance: 0.00199 USDT

Orders:
  BUY 6.2279674364331195 XRP/ETH @ 0.00234478
```

To get it to actually execute trades if needed:

```
$ crypto_reflex --force --trade binance
Connected to exchange: binance

Current Portfolio:
  XRP    3272.28  (39.96 / 40.00%)
  BTC    0.14     (20.04 / 20.00%)
  ETH    3.84     (19.94 / 20.00%)
  BNB    22.94    (10.04 / 10.00%)
  USDT   262.48   (10.02 / 10.00%)

  Total value: 2619.01 USDT
  Balance error: 0.043 / 0.08

Balancing needed [FORCED]:

Proposed Portfolio:
  XRP    3272.28  (39.96 / 40.00%)
  BTC    0.14     (20.04 / 20.00%)
  ETH    3.85     (20.00 / 20.00%)
  BNB    22.80    ( 9.98 / 10.00%)
  USDT   262.48   (10.02 / 10.00%)

  Total value: 2619.01 USDT
  Balance error: 0.031 / 0.08
  Total fees to re-balance: 0.001592 USDT

Orders:
  Submitted: sell 0.13 BNB/ETH @ 0.08422
```
## Running automatically

You can set this to run in a cron job on a unix system by putting something along the lines of (adjust for your path and email address) below
in your crontab file:

```
MAILTO=matt@example.com
*/5 * * * * OUTPUT=`cd /home/matt/crypto_reflex; bin/crypto_reflex --trade binance`; echo "$OUTPUT" | grep -q "No balancing needed" || echo "$OUTPUT"
```

This will run the script every 5 minutes and will email you only if some balancing (or an error) occurs.
