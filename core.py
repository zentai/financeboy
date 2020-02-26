import sys
import logging
import pandas as pd
import datetime
from datetime import timedelta

import matplotlib.pyplot as plt
from investment.reits import Reits


logformat = "%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s"
datefmt = "%m-%d %H:%M"

logging.basicConfig(filename="app.log", level=logging.INFO, filemode="w",
                    format=logformat, datefmt=datefmt)

stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(logging.Formatter(fmt=logformat, datefmt=datefmt))

logger = logging.getLogger("app")
logger.addHandler(stream_handler)


class Profile(object):
    """
    1. we have cash
    2. we have holding CODE - Quantity
    3. we have trasaction history: date, id, strike_price, Quantity, cost
    """
    def __init__(self, cash=0):
        self.init_cash = cash
        self.cash = cash
        self.holding = {}
        self.base_unit = 100.
        self.profolio = pd.DataFrame(columns=['Code', 'Dividends',
                                              'Strike', 'Total.Div', 'BuyAll',
                                              'Holding'])

    def strategy_dividends_show_hand(self, date, code, dividend, strike):

        total_dividends = self.holding.get(code, 0) * dividend

        self.dividends(code, dividend)
        available_buy = self._cash_to_unit(strike)
        self.buy_all(code, strike)

        self.profolio.loc[date] = [code, dividend, strike, total_dividends,
                              available_buy,
                              self.holding.get(code, 0)]

    def dividends(self, code, cash):
        quantity = self.holding.get(code, 0)
        # logger.info('Code: %s, q: %s, cash: %s', code, quantity, cash * quantity)
        self.cash += cash * quantity


    def _cash_to_unit(self, strike):
        return int(self.cash / strike / self.base_unit) * self.base_unit

    def buy_all(self, code, strike):
        unit = self._cash_to_unit(strike)
        self.buy(code, strike, unit)

    def buy(self, code, strike, quantity, verbose=False):
        self.holding[code] = self.holding.get(code, 0) + quantity
        self.cash -= strike * quantity
        if verbose:
            logger.info('buy, %s, %s, %s, %s', code, strike, quantity, self.holding[code])

    def show_hand(self, code, strike):
        return (self.holding.get(code) * strike) + self.cash

    def performance(self, code, strike):
        return self.holding.get(code)
        # spot = self.show_hand(code, strike)
        # yield_percent = (spot/self.init_cash - 1) * 100
        # return yield_percent


def back_trace(reits, start_date=None, end_date=None):
    p = Profile(cash=10000)
    buy_price = reits.first_price
    sell_price = reits.strike


    p.buy_all(code, buy_price)

    for index, row in reits.mix_df.iterrows():
        p.strategy_dividends_show_hand(index, code, row['Dividends'], row['Close'])
    # logger.info('Code: %s, IN: %s, Out: %s, yield: %s', code, buy_price, sell_price, p.performance(code, sell_price))
    return p, reits


def get_codes(start_date=None, end_date=None):
    code = {
            'SV3U.SI': Reits('SV3U.SI', start_date, end_date),
            'M1GU.SI': Reits('M1GU.SI', start_date, end_date),
            'P40U.SI': Reits('P40U.SI', start_date, end_date),
            'AW9U.SI': Reits('AW9U.SI', start_date, end_date),
            'A68U.SI': Reits('A68U.SI', start_date, end_date),
            'A17U.SI': Reits('A17U.SI', start_date, end_date),
            'N2IU.SI': Reits('N2IU.SI', start_date, end_date),
            'T82U.SI': Reits('T82U.SI', start_date, end_date),
            'SK6U.SI': Reits('SK6U.SI', start_date, end_date),
            'J69U.SI': Reits('J69U.SI', start_date, end_date),
            'C38U.SI': Reits('C38U.SI', start_date, end_date),
            'K71U.SI': Reits('K71U.SI', start_date, end_date)
            }
    return code

# independ strategy(swapable)
# input (cash, strike, dividends), output(buy)

def load(code):
    return get_codes().get(code).hist_price_df


if __name__ == '__main__':

    df = pd.DataFrame(columns=['code', 'close_mean', 'close_std', 'div_mean', 'div_std', 'years', 'performance', 'start_price', 'end_price', 'sharp_ratio', 'min_q'])
    # codes = get_codes(start_date='2018-01-01', end_date='2019-03-01')
    codes = get_codes()
    for i, code in enumerate(codes):
        profile, reits = back_trace(codes.get(code))
        df.loc[i] = (code, reits.close_mean, reits.close_std,
                     reits.dividends_mean, reits.dividends_std, reits.years,
                     profile.performance(code, reits.strike)/reits.years,
                     reits.first_price, reits.strike, reits.sharp_ratio, reits.min_q)
        # df.loc[i] = run(reits.get(code))
    # df['yield'] = (df['div_mean'] / df['close_mean']) * 100
    # df['div_confidence'] = (df['div_std'] / df['div_mean']) * 100
    # df['P/E'] = df['end_price'] / df['div_mean']
    # df['Risk'] = (df['close_std'] / df['close_mean']) * (df['div_std'] / df['div_mean'])
    df['yield'] = df['div_mean']/df['close_mean']
    df['m'] = (df['end_price'] - df['start_price']) / (df['years'] - 0)
    df['close_std_perct'] = df['close_std'] / df['close_mean']
    # df['div_std_perct'] = df['div_std'] / df['div_mean']
    # df = df.sort_values(by=['close_std_perct', 'div_std_perct', 'performance'])
    df = df.sort_values(by=[ 'performance', 'div_mean'])
    print(df)



    # print df[['code','performance', 'div_std_perct', 'close_std_perct', 'min_q']]

    # print df.sort_values(by=['years', 'performance', 'risk'])
    # print df.sort_values(by=['div_mean', 'div_std'])
"""

if __name__ == '__main__':
    initial = 2000
    # initial = 30000 + 10000
    p = Profile(cash=initial)
    buy_price = 1
    sell_price = 1
    dividends = 0.06
    code = 'code'

    p.buy_all(code, buy_price)
    monthly_input = 4000
    topup = monthly_input * 12
    level = 1
    salary = 8000
    print 'Initial: %s, topup: %s' % (initial, monthly_input)
    for i in xrange(1, 50):
        p.dividends(code, dividends)
        p.cash += topup
        p.buy_all(code, buy_price)
        holding = p.holding[code]
        holding_value = holding * dividends
        mark = ''
        while holding_value > (level * salary):
            level += 1
            mark = '      <====== Lv %s' % (level - 1 )
        print '[%s] holding: %s, dividends: %s %s' % ( i, holding, holding_value, mark)

"""