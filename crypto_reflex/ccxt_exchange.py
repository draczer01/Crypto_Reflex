import ccxt, os

from functools import lru_cache

exchanges = ccxt.exchanges


class CCXTExchange():

    def __init__(self, name, currencies, api_key, api_secret):
        self.name = name
        self.currencies = currencies
        self.exch = getattr(ccxt, name)({'nonce': ccxt.Exchange.milliseconds})
        if os.getenv("PROXY_URL") is not None:
            self.exch.proxies= {
                "http"  : os.environ.get('PROXY_URL', ''),
                "https" : os.environ.get('PROXY_URL', '')
            }
        self.exch.apiKey = api_key
        self.exch.secret = api_secret
        self.exch.load_markets()

    @property
    @lru_cache(maxsize=None)
    def balances(self):
        bals = self.exch.fetch_balance()['total']
        return {k: bals[k] for k in self.currencies}

    @property
    @lru_cache(maxsize=None)
    def pairs(self):
        _pairs = []
        for i in self.currencies:
            for j in self.currencies:
                pair = "{}/{}".format(i, j)
                if pair in self.exch.markets and self.exch.markets[pair]['active']:
                    _pairs.append(pair)
        return _pairs

    @property
    @lru_cache(maxsize=None)
    def rates(self):
        _rates = {}
        if self.exch.has['fetchTickers']:
            tickers = self.exch.fetchTickers()
        else:
            tickers = {}

        for pair in self.pairs:
            if tickers:
                high = tickers[pair]['ask']
                low = tickers[pair]['bid']
            else:
                orderbook = self.exch.fetchOrderBook(pair)
                high = orderbook['asks'][0][0]
                low = orderbook['bids'][0][0]
            mid = (high + low) / 2.0
            _rates[pair] = {'mid': mid,
                            'high': high,
                            'low': low, }

        return _rates

    @property
    @lru_cache(maxsize=None)
    def limits(self):
        return {pair: self.exch.markets[pair]['limits']
                for pair in self.pairs}

    @property
    @lru_cache(maxsize=None)
    def fee(self):
        return self.exch.fees['trading']['maker']

    def preprocess_order(self, order):
        try:
            limits = self.limits[order.pair]
        except KeyError:
            return None

        order.amount = float(
            self.exch.amount_to_precision(
                order.pair, order.amount))
        order.price = float(
            self.exch.price_to_precision(
                order.pair, order.price))

        if order.price == 0 or order.amount == 0:
            return None

        if order.amount < limits['amount']['min'] \
           or order.amount * order.price < limits['cost']['min']:
            return None
        order.type_ = 'LIMIT'
        return order

    def execute_order(self, order):
        if not order.type_:
            raise ValueError("Order needs preprocessing first")
        return self.exch.create_order(order.pair,
                                      order.type_,
                                      order.direction,
                                      order.amount,
                                      order.price)

    def cancel_orders(self):
        cancelled_orders = []
        for pair in self.pairs:
            open_orders = self.exch.fetch_open_orders(symbol=pair)
            for order in open_orders:
                self.exch.cancel_order(order['id'], order['symbol'])
                cancelled_orders.append(order)
        return cancelled_orders
