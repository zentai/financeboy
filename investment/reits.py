import logging
import pandas as pd
import datetime


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