import sys
import logging
import pandas as pd
import datetime
from datetime import timedelta

import matplotlib.pyplot as plt


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


class Reits(object):
    def __init__(self, code, start_date=None, end_date=None):
        self.code = code
        self.years = 0
        self.strike = 0
        self.close_mean = 0
        self.close_std = 0
        self.dividends_mean = 0
        self.dividends_std = 0
        self.first_day = None
        self.first_price = 0.0
        self.last_day = None
        self.hist_price_df = None
        self.dividends_df = None
        self.mix_df = None
        self.risk = 0.0
        # POC
        self.min_q = 0

        # calc data
        self.reload(code, start_date, end_date)


    def reload(self, code, start_date, end_date):
        self.hist_price_df = pd.read_csv('data/history_price/%s.csv' % code,
                                         index_col=0, na_filter=True)

        self.hist_price_df.sort_index(inplace=True)
        self.hist_price_df = self.hist_price_df.fillna(method='ffill')

        self.dividends_df = pd.read_csv('data/dividends/%s.csv' % code,
                                        index_col=0, na_filter=True)

        self.dividends_df.sort_index(inplace=True)

        self.mix_df = self.dividends_df.join(self.hist_price_df)
        self.mix_df.sort_index(inplace=True)
        self.mix_df = self.mix_df.fillna(method='ffill', axis='columns')

        # Time machine
        if start_date and end_date:
            self.mix_df = self.mix_df.loc[start_date:end_date]
            self.hist_price_df = self.hist_price_df.loc[start_date:end_date]
            self.dividends_df = self.dividends_df.loc[start_date:end_date]
        elif start_date:
            self.mix_df = self.mix_df.loc[start_date:]
            self.hist_price_df = self.hist_price_df.loc[start_date:]
            self.dividends_df = self.dividends_df.loc[start_date:]
        elif end_date:
            self.mix_df = self.mix_df.loc[:end_date]
            self.hist_price_df = self.hist_price_df.loc[:end_date]
            self.dividends_df = self.dividends_df.loc[:end_date]
        else:
            pass

        date_serials = sorted(self.hist_price_df.index.values)
        self.first_day = date_serials[0]
        self.last_day = date_serials[-1]
        self.first_price = self.hist_price_df.iloc[0].Close
        self.strike = self.hist_price_df.iloc[-1].Close
        self.years = self._year_to_date(self.first_day)
        self.dividends_mean, self.dividends_std = self._avg_dividends()
        self.close_mean, self.close_std = self._avg_price()
        # self.risk = (((self.strike - self.close_mean) / self.close_std)) * 100.
        # self.risk = self.strike / (self.close_std + self.close_mean)
        # self.risk = self.strike / (self.close_mean + self.close_std)
        self.sharp_ratio = self.sharp_ratio()
        self.min_q = int(1. / (self.dividends_mean / self.strike) * 100)
        # min_q, the baseline Q which year dividends can buy 1 lot

    def sharp_ratio(self):
        adj_close = self.hist_price_df['Adj Close']
        pct_change = adj_close.pct_change()
        profit = pct_change.mean()
        risk = pct_change.std()

        rolling_profit = pct_change.rolling(252).mean()
        rolling_risk = pct_change.rolling(252).std()
        self.hist_price_df['sharp_ratio'] = rolling_profit / rolling_risk * (252 ** 0.5)

        return profit / risk * (252 ** 0.5)


    def _sig_count(sig):
        lower_bound = self.close_mean - (self.close_std * sig)
        upper_bound = self.close_mean + (self.close_std * sig)

        return 0

    def _year_to_date(self, date_str):
        return (datetime.datetime.today() - datetime.datetime.strptime(date_str,
                "%Y-%m-%d")).days / 365


    def _avg_dividends(self):
        resample_div = self.dividends_df.groupby(
            pd.PeriodIndex(self.dividends_df.index, freq='A'), axis=0).sum()
        return resample_div['Dividends'].mean(), resample_div['Dividends'].std(ddof=0)


    def _avg_price(self):
        return self.hist_price_df['Close'].mean(), self.hist_price_df['Close'].std(ddof=0)


# def plot(code):

#     plt.figure()
#     df.plot(x='code', y='close_mean')
#     plt.show()

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
            # 'M1GU.SI': Reits('M1GU.SI', start_date, end_date),
            # 'P40U.SI': Reits('P40U.SI', start_date, end_date),
            # 'AW9U.SI': Reits('AW9U.SI', start_date, end_date),
            # 'A68U.SI': Reits('A68U.SI', start_date, end_date),
            # 'A17U.SI': Reits('A17U.SI', start_date, end_date),
            'N2IU.SI': Reits('N2IU.SI', start_date, end_date),
            # 'T82U.SI': Reits('T82U.SI', start_date, end_date),
            'SK6U.SI': Reits('SK6U.SI', start_date, end_date),
            # 'J69U.SI': Reits('J69U.SI', start_date, end_date),
            # 'C38U.SI': Reits('C38U.SI', start_date, end_date),
            # 'K71U.SI': Reits('K71U.SI', start_date, end_date)
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