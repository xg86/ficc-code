import QuantLib as ql
import numpy as np
import pandas as pd
from datetime import datetime

def cacualte_pd(cds_spread, recovery_rate, maturity):
    cds_spread = cds_spread/10000
    recovery_rate = recovery_rate/100
    #maturity = ql.Period(maturity, ql.Years)
    #day_counter = ql.Actual365Fixed()
    #maturity = day_counter.yearFraction(maturity, date)

    hazard_rate = cds_spread/(1 - recovery_rate)
    default_prob_curve = ql.FlatHazardRate(0,
                                           ql.NullCalendar(),
                                           ql.QuoteHandle(ql.SimpleQuote(hazard_rate)),
                                           ql.Actual365Fixed())
    survival_probability = default_prob_curve.survivalProbability(maturity)
    return  1 - survival_probability

'''
cds_spread =150
recovery_rate = 40
maturity = 5.0
'''
cds_spread = 40.1702  # 200 bps = 2%
maturity = 1.6219  # 3 years
recovery_rate = 20  # 40% recovery rate

pd = cacualte_pd(cds_spread, recovery_rate, maturity)
print(f"PD is : {pd:.4%}")