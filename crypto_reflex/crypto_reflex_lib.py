import logging
import sys
import json

from crypto_reflex.simple_balancer import SimpleBalancer
from crypto_reflex.ccxt_exchange import CCXTExchange
from crypto_reflex.executor import Executor
from crypto_reflex.portfolio import Portfolio

logger = logging.getLogger(__name__)


def crypto_reflex_lib(exchange, target, api_key, api_secret, threshold, valuebase='USDT', trade=False, max_orders=5, force=False, mode='mid', j=True):
    

    try:

        targets = json.loads(str(target))

    except ValueError:
        logger.error("Targets format invalid")
        sys.exit(1)
 
    total_target = sum(targets.values())
    if total_target != 100:
        logger.error("Total target needs to equal 100, it is {}"
                     .format(total_target))
        sys.exit(1)

    valuebase = valuebase

    exchange = CCXTExchange(exchange,
                            targets.keys(),
                            api_key,
                            api_secret)
    if j == False:
        print("Connected to exchange: {}".format(exchange.name))
        print()    

    portfolio = Portfolio.make_portfolio(targets, exchange, threshold, valuebase)
    if j == False:
        print("Current Portfolio:")
    for cur in portfolio.balances:
        bal = portfolio.balances[cur]
        pct = portfolio.balances_pct[cur]
        tgt = targets[cur]
        if j == False:
            print("  {:<6s} {:<8.2f} ({:>5.2f} / {:>5.2f}%)"
                .format(cur, bal, pct, tgt))

            print()
            print("  Total value: {:.16f} {}".format(portfolio.valuation_quote,
                                            portfolio.quote_currency))
    balancer = SimpleBalancer()
    executor = Executor(portfolio, exchange, balancer)
    res = executor.run(force=force,
                       trade=trade,
                       max_orders=max_orders,
                       mode=mode)
    if j == False:
        print("  Balance RMS error: {:.2g} / {:.2g}".format(
            res['initial_portfolio'].balance_rms_error,
            threshold))

        print("  Balance Max error: {:.2g} / {:.2g}".format(
            res['initial_portfolio'].balance_max_error,
            threshold))
    
        print()
    if not portfolio.needs_balancing and not force:
        print("No balancing needed")
        sys.exit(0)
    if j == False:
        print("Balancing needed{}:".format(" [FORCED]" if force else ""))
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
        if j == False:
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
    if j == False:
        print("  Total fees to re-balance: {} {}"
            .format(total_fee,
                    portfolio.quote_currency))

        print()
        print("Orders:")
        if trade:
            for order in res['success']:
                print("  Submitted: {}".format(order))

            for order in res['errors']:
                print("  Failed: {}".format(order))
        else:
            for order in res['orders']:
                print("  " + str(order))


    if j:
        return json.dumps({"portfolio_value": portfolio.valuation_quote, "currency": portfolio.quote_currency, "cost": total_fee})


