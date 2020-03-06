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
