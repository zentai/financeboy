import sys
import yaml
import datetime
import logging

from pandas.io.json import json_normalize
from yahoofinancials import YahooFinancials


def fetch(meta_path='data/meta.yaml'):
    logger = logging.getLogger(__name__)

    with open(meta_path) as stream:
        metas = yaml.load(stream)

    for fname, meta in metas.items():
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
        logger.info('Download: {fname}'.format(fname=fname))
        logger.debug('Meta: {meta}'.format(meta=meta))


if __name__ == '__main__':
    import reload
    reload.fetch()