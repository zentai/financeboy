import yaml
import datetime

from pandas.io.json import json_normalize
from yahoofinancials import YahooFinancials

def load_meta():
    with open('data/meta.yaml') as stream:
        return yaml.load(stream)

def main():
    metas = load_meta()
    for fname, meta in metas.iteritems():
        print fname, meta
        print '-' * 20

        code = meta['code']
        start = str(meta['start'])
        end = datetime.datetime.today().strftime('%Y-%m-%d')

        yahoo_finance = YahooFinancials(code)
        daily_price = yahoo_finance.get_historical_price_data(start, end, 'daily')

        df = json_normalize(daily_price[code]['prices'])
        df = df.drop(['date'], axis=1)
        df = df.rename(index=str, columns={'formatted_date': 'Date',
                                           'open': 'Open',
                                           'high': 'High',
                                           'low': 'Low',
                                           'close': 'Close',
                                           'adjclose': 'Adj Close',
                                           'volume': 'Volume',
                                           })
        df = df.round(decimals=2)

        df.to_csv(path_or_buf='data/history_price/%s' % fname,
                  index=False,
                  columns=['Date', 'Open', 'High', 'Low', 'Close',
                           'Adj Close', 'Volume'])


if __name__ == '__main__':
    main()