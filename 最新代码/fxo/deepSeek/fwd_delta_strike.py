import QuantLib as ql
import math
import numpy as np
import matplotlib.pyplot as plt

# Set evaluation date
calculation_date = ql.Date(31, 10, 2024)
ql.Settings.instance().evaluationDate = calculation_date

# Market data
spot = 7.12  # USDCNY spot rate
domestic_rate = 2.122/100  # CNY rate (domestic)
foreign_rate = 4.3465/100   # USD rate (foreign)
volatility = 6.0722/100      # 10% volatility
maturity_date = ql.Date(4, 11, 2027)
day_count = ql.Actual365Fixed()
option_type = ql.Option.Put  # or ql.Option.Put
target_delta = -0.15  # Target forward delta

# Setup curves and process
domestic_curve = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, domestic_rate, day_count))
foreign_curve = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, foreign_rate, day_count))
fx_spot = ql.QuoteHandle(ql.SimpleQuote(spot))
#vol_handle = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, ql.NullCalendar(), volatility, day_count))

#process = ql.GeneralizedBlackScholesProcess(fx_spot, foreign_curve, domestic_curve, vol_handle)

# Time to maturity and forward price
T = day_count.yearFraction(calculation_date, maturity_date)
F = spot * (foreign_curve.discount(T) / domestic_curve.discount(T))  # Forward price
#print(f"F in : {F:.4f}")
#print(f"T in : {T:.4f}")

def delta_forward(strike):
    #print(f"Strike in delta_forward: {strike:.4f}")
    stdev = volatility * math.sqrt(T)
    d1 = (math.log(F / strike) + 0.5 * volatility**2 * T) / stdev
    #print(f"d1 in delta_forward: {d1:.4f}")
    cnd = ql.CumulativeNormalDistribution()
    cdn_val = cnd(d1)
    if option_type == ql.Option.Call:
        return cdn_val
    else:
        return cdn_val - 1

# Solve for strike using Brent's method with correct bounds
solver = ql.Brent()
solver.setMaxEvaluations(1000)
accuracy = 1e-6
guess = F
lower = F * 0.9 # 10% of forward as lower bound
upper = F * 1.1  # 200% of forward as upper bound

strike = solver.solve(lambda k: delta_forward(k) - target_delta, accuracy, guess, lower, upper)
print(f"Strike for {target_delta*100}D forward delta: {strike:.4f}")
