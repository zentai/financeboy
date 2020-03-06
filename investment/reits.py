import logging
import pandas as pd
import datetime
from investment.algo import DCF

# report field
Code                = 'Code'
Years               = 'Years'
First_Price         = 'First Price'
Strike              = 'Strike'
PE                  = 'P/E'
Close_Mean          = 'Close Mean'
Close_Stdv          = 'Close Stdv'
Dividend_Mean       = 'Dividend Mean'
Dividend_Stdv       = 'Dividend Stdv'
Dividend_Stdv_pect  = 'Dividend Stdv %'
Mean_Q              = 'Mean Q'
Sharpe_Ratio        = 'Sharpe Ratio'
Yield               = 'Yield'
Risk                = 'Risk'
M                   = 'M'
Sig_count           = 'Sig_count'
DCF_price           = 'DCF price'
DCF_Flag            = 'DCF B/S Flag'


# Algo difination
def sig_count(sig, close_mean, close_std):
    lower_bound = close_mean - (close_std * sig)
    upper_bound = close_mean + (close_std * sig)
    return lower_bound, upper_bound


def sharpe_ratio(hist_price_df):
    adj_close = hist_price_df['Adj Close']
    pct_change = adj_close.pct_change()
    profit = pct_change.mean()
    risk = pct_change.std()

    rolling_profit = pct_change.rolling(252).mean()
    rolling_risk = pct_change.rolling(252).std()
    # FIXME:
    # should we using sharpe with moving windows?
    # hist_price_df['sharpe_ratio'] = rolling_profit / rolling_risk * (252 ** 0.5)

    return profit / risk * (252 ** 0.5)


def dividend_mean(dividends_df):
    resample_div = dividends_df.groupby(
        pd.PeriodIndex(dividends_df.index, freq='A'), axis=0).sum()
    return resample_div['Dividends'].mean(), resample_div['Dividends'].std(ddof=0)


class ReitsEnrichment(object):


    def __init__(self, reits):
        self._reits = reits
        dividends_mean, dividends_std = dividend_mean(reits.dividends_df)
        close_mean = reits.hist_price_df['Close'].mean()
        close_std = reits.hist_price_df['Close'].std(ddof=0)

        dcf = DCF()
        price_range = dcf.price(strike=reits.strike, PE=1, dividend=
                                dividends_mean, years=10)
        price_range = list(map(lambda x: round(x, 2), price_range))

        self.report = {
            Code                : reits.code,
            Years               : reits.years,
            First_Price         : reits.first_price,
            Strike              : reits.strike,
            PE                  : reits.strike / dividends_mean,
            Close_Mean          : close_mean,
            Close_Stdv          : close_std,
            Dividend_Mean       : dividends_mean,
            Dividend_Stdv       : dividends_std,
            Dividend_Stdv_pect  : dividends_std / dividends_mean,
            Sharpe_Ratio        : sharpe_ratio(reits.hist_price_df),
            Yield               : dividends_mean / close_mean,
            Risk                : (reits.strike - close_mean) / close_std,
            M                   : (reits.strike - reits.first_price) / reits.years,
            Sig_count           : sig_count(1, close_mean, close_std), # not sure
            DCF_price           : price_range,
            DCF_Flag            : reits.strike / price_range[1]
        }


    def projection(self, fields):
        return [self.report.get(field, None) for field in fields]


class Reits(object):
    def __init__(self, code, start_date=None, end_date=None):
        self.code = code
        self.years = 0
        self.strike = 0his
        self.first_day = None
        self.first_price = 0.0
        self.last_day = None
        self.hist_price_df = None
        self.dividends_df = None
        self.mix_df = None

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


    def _year_to_date(self, date_str):
        return (datetime.datetime.today() - datetime.datetime.strptime(date_str,
                "%Y-%m-%d")).days / 365


    def history_price(self):
        self.hist_price_df['Close'].plot()


    def history_dividend(self):
        self.dividends_df['Dividends'].plot()


    def mixchart(self):
        self.mix_df.plot()