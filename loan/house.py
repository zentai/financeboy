#!/Users/Zen/code/finlab/env/bin/python
# -*- coding: utf-8 -*-
import math
import calendar
import datetime

import pandas as pd

'''
1. 每個月供 x 元多久可以結束，總利息多少
2. 跟原本的比較，節省多少利息
3.
'''

def _calc_fv(pv, rate, m, days):
# def _calc_fv(pv=480000, rate=0.0452, m=365, days=31):
    """pv = HouseLoan
       rate = percentage 4.52%
       m = term, 365
       days = days
    """
    fv = pv * math.pow((1 + rate/m), days)
    interest = fv - pv
    return fv, interest


def monthly_end_day(start_year, end_year):
    eod = []
    for y in range(start_year,end_year+1):
        eod += [calendar.monthrange(y, i)[1] for i in range(1, 13)]
    return eod


def run(pv=465623.95, rate=0.0452, installment=2210):
    m = 365 # re-calc interest times per years
    year = start_year = datetime.datetime.now().year
    total_interest = 0
    history = pd.DataFrame(columns=['Balance', 'Monthly Interest', 'years', 'total_interest'])
    month = 1
    for days in monthly_end_day(year, year+35):
        fv, interest = _calc_fv(pv, rate, m, days)
        total_interest += interest
        history.loc[datetime.datetime(year, month, 1)] = [fv, interest, year - start_year + 1, total_interest]
        month = month+1 if month < 12 else 1
        pv = fv
        pv -= installment
        if pv < 0:
            return (year - start_year), total_interest, history


def default():
    pv = 466136.39 - 40000
    installment = 6000
    origin_installment_plan = run(pv=pv, rate=0.0452, installment=installment)
    new_installment_plan = run(pv=pv, rate=0.0427, installment=installment)
    print("years: %s, total: %s" % origin_installment_plan[:-1])
    print("years: %s, total: %s" % new_installment_plan[:-1])


if __name__ == '__main__':
    default()
