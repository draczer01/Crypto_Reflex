import argparse
import configparser
import logging
import sys
import json

from crypto_reflex.simple_balancer import SimpleBalancer
from crypto_reflex.ccxt_exchange import CCXTExchange, exchanges
from crypto_reflex.executor import Executor
from crypto_reflex.portfolio import Portfolio

logger = logging.getLogger(__name__)


def main(args=None):
    config = configparser.ConfigParser()
    config.read('config.ini')

    def exchange_choices():
        return set(config.sections()) & set(exchanges)

    parser = argparse.ArgumentParser(
        description='Balance holdings on an exchange.')
    parser.add_argument('--trade', action="store_true",
                        help='Actually place orders')
    parser.add_argument('-j','--json', action='store_true',
                        help='returns the data as a json')
    parser.add_argument('--force', action="store_true",
                        help='Force rebalance')
    parser.add_argument('--max_orders', default=5,
                        help='Maximum number of orders to perform in '
                             'rebalance')
    parser.add_argument('--valuebase', default='USDT',
                        help='Currency to value portfolio in')
    parser.add_argument('--cancel', action="store_true",
                        help='Cancel open orders first')
    parser.add_argument('--mode', choices=['mid', 'passive', 'cheap'],
                        default='mid',
                        help='Mode to place orders')
    parser.add_argument('exchange', choices=exchange_choices())
    args = parser.parse_args()

    config = config[args.exchange]

    try:
        targets = [x.split() for x in config['targets'].split('\n')]
        targets = dict([[a, float(b)] for (a, b) in targets])
    except ValueError:
        logger.error("Targets format invalid")
        sys.exit(1)

    total_target = sum(targets.values())
    if total_target != 100:
        logger.error("Total target needs to equal 100, it is {}"
                     .format(total_target))
        sys.exit(1)

    valuebase = config.get('valuebase') or args.valuebase

    exchange = CCXTExchange(args.exchange,
                            targets.keys(),
                            config['api_key'],
                            config['api_secret'])
    if args.json == False:
        print("Connected to exchange: {}".format(exchange.name))
        print()

    if args.cancel:
        print("Cancelling open orders...")
        for order in exchange.cancel_orders():
            print("Cancelled order:", order['symbol'], order['id'])
        print()

    threshold = float(config['threshold'])
    max_orders = int(args.max_orders)

    portfolio = Portfolio.make_portfolio(targets, exchange, threshold, valuebase)
    curr_portafolio = portfolio
    if args.json == False:
        print("Current Portfolio:")
    for cur in portfolio.balances:
        bal = portfolio.balances[cur]
        pct = portfolio.balances_pct[cur]
        tgt = targets[cur]
        if args.json == False:
            print("  {:<6s} {:<8.2f} ({:>5.2f} / {:>5.2f}%)"
                .format(cur, bal, pct, tgt))

            print()
            print("  Total value: {:.16f} {}".format(portfolio.valuation_quote,
                                            portfolio.quote_currency))
    balancer = SimpleBalancer()
    executor = Executor(portfolio, exchange, balancer)
    res = executor.run(force=args.force,
                       trade=args.trade,
                       max_orders=max_orders,
                       mode=args.mode)
    if args.json == False:
        print("  Balance RMS error: {:.2g} / {:.2g}".format(
            res['initial_portfolio'].balance_rms_error,
            threshold))

        print("  Balance Max error: {:.2g} / {:.2g}".format(
            res['initial_portfolio'].balance_max_error,
            threshold))
    
        print()
    if not portfolio.needs_balancing and not args.force:
        print("No balancing needed")
        sys.exit(0)
    if args.json == False:
        print("Balancing needed{}:".format(" [FORCED]" if args.force else ""))
        print()
        print("Proposed Portfolio:")
    portfolio = res['proposed_portfolio']

    if not portfolio:
        print("Could not calculate a better portfolio")
        sys.exit(0)

    for cur in portfolio.balances:
        bal = portfolio.balances[cur]
        pct = portfolio.balances_pct[cur]
        tgt = targets[cur]
        if args.json == False:
            print("  {:<6s} {:<8.16f} ({:>5.16f} / {:>5.16f}%)"
                .format(cur, bal, pct, tgt))

            print()
            print("  Total value: {:.2f} {}".format(portfolio.valuation_quote,
                                            portfolio.quote_currency))
            print("  Balance RMS error: {:.2g} / {:.2g}".format(
                res['proposed_portfolio'].balance_rms_error,
                threshold))

            print("  Balance Max error: {:.2g} / {:.2g}".format(
                res['proposed_portfolio'].balance_max_error,
                threshold))

    total_fee = '%s' % float('%.4g' % res['total_fee'])
    if args.json == False:
        print("  Total fees to re-balance: {} {}"
            .format(total_fee,
                    portfolio.quote_currency))

        print()
        print("Orders:")
        if args.trade:
            for order in res['success']:
                print("  Submitted: {}".format(order))

            for order in res['errors']:
                print("  Failed: {}".format(order))
        else:
            for order in res['orders']:
                print("  " + str(order))


    if args.json:
        return json.dumps({"portfolio_value": portfolio.valuation_quote, "currency": portfolio.quote_currency, "cost": total_fee})

if __name__ == '__main__':
    main()
