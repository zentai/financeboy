import yaml
import logging.config
import os
import logging
import sys
import pandas as pd
import datetime
from datetime import timedelta

import matplotlib.pyplot as plt
from investment.reits import Reits, ReitsReporter
from investment.algo import DCF
from core import get_codes



def set_log_cfg(default_path="log_cfg.yaml", default_level=logging.INFO, env_key="LOG_CFG"):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "r") as f:
            config = yaml.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

def usecase():

    # df = pd.DataFrame(columns=['code', 'close_mean', 'close_std', 'div_mean', 'div_std', 'years', 'performance', 'start_price', 'end_price', 'sharp_ratio', 'min_q'])
    df = pd.DataFrame(columns=['code', 'div_mean', 'div_std', 'years', 'start_price', 'end_price', 'price range', 'B/S flag', 'sharp_ratio'])
    # codes = get_codes(start_date='2018-01-01', end_date='2019-03-01')
    codes = get_codes()
    dcf = DCF()
    for i, code in enumerate(codes):
        reits = codes.get(code)

        price_range = dcf.price(strike=reits.strike, PE=1, dividend=reits.  
                                dividends_mean, years=10)
        price_range = list(map(lambda x: round(x, 2), price_range))

        # price_range = map(lambda x: round(x, 2), price_range)
        buy_sell_indicator = reits.strike / price_range[1]

        df.loc[i] = (code, reits.dividends_mean, reits.dividends_std, reits.years, reits.first_price, reits.strike, price_range, buy_sell_indicator, reits.sharp_ratio)
        # df.loc[i] = run(reits.get(code))
    # df['yield'] = (df['div_mean'] / df['close_mean']) * 100
    # df['div_confidence'] = (df['div_std'] / df['div_mean']) * 100
    # df['P/E'] = df['end_price'] / df['div_mean']
    # df['Risk'] = (df['close_std'] / df['close_mean']) * (df['div_std'] / df['div_mean'])
    df['yield'] = df['div_mean']/df['end_price']
    df['m'] = (df['end_price'] - df['start_price']) / (df['years'] - 0)
    df = df.sort_values(by=[ 'B/S flag'])
    print(df)
    # reits = codes.get('M1GU.SI')
    reits = codes.get('SV3U.SI')
    reits.mixchart()
    # reits.history_price()
    # reits.history_dividend()
    plt.show()
    # print(reits.dividends_df)
    # plot_stock(reits.dividends_df, 'Dividends')


def plot_stock(df, y_axis):
    df[y_axis].plot()
    plt.show()

if __name__ == '__main__':
    import reload
    set_log_cfg(default_path='conf/logging.yaml')
    # reload.fetch()
    # usecase()
    codes = get_codes()
    reits = codes.get('SV3U.SI')
    rr = ReitsReporter(reits)
    print(rr.algo_mapping)
    # print(rr.algo_mapping.get('P/E'))



