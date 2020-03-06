import os
import sys
import logging
import logging.config
import yaml
import datetime
from datetime import timedelta

import pandas as pd
import matplotlib.pyplot as plt

from investment.reits import *
from investment.algo import DCF


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

def usecase_reits_plot():
    r = Reits('M1GU.SI')  # code define at meta.yaml
    r.history_price()
    plt.show()

def usecase_reits_table():
    report_fields = [Code,
                        Dividend_Mean,
                        Dividend_Stdv,
                        Dividend_Stdv_pect,
                        Years,
                        PE,
                        First_Price,
                        Strike,
                        DCF_price,
                        DCF_Flag,
                        Sharpe_Ratio]

    df = pd.DataFrame(columns=report_fields)
    codes = get_codes()
    for i, code in enumerate(codes):
        reits = codes.get(code)
        df.loc[i] = ReitsEnrichment(reits).projection(report_fields)
    df = df.sort_values(by=['DCF B/S Flag'])
    print(df)


if __name__ == '__main__':
    import reload
    set_log_cfg(default_path='conf/logging.yaml')
    # reload.fetch()
    usecase_reits_table()
    usecase_reits_plot()
