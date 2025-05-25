import numpy as np
from scipy.stats import norm
from datetime import datetime, date
import pandas as pd

# Helper functions
def ppf(x):
    return norm.ppf(x)

def N(x):
    return norm.cdf(x)

# Define GK function
def GK(F, K, days_to_expiry, days_to_delivery, ccy1, ccy2, sigma):
    d1 = (np.log(F/K) + 0.5*sigma**2*days_to_expiry/365) / (sigma*np.sqrt(days_to_expiry/365))
    d2 = d1 - sigma*np.sqrt(days_to_expiry/365)
    c = np.exp(-ccy2*days_to_delivery/365)*(F*N(d1) - K*N(d2))
    delta_spot = np.exp(-ccy1*days_to_expiry/365) * N(d1)
    delta_fwd = N(d1)
    return c, delta_fwd, delta_spot

# Inputs
s = 1.0615
pts = 60.1
fwd_scale = 10**4
f = s + pts / fwd_scale
print(f"Forward = {f}")

k = 1.101
sigma = 0.089
ccy1 = 0.0255008  # EUR
ccy2 = 0.0478     # USD

# Date calculations
price_dt = date(2023, 3, 16)
premium_dt = date(2023, 6, 20)
expiry_dt = date(2023, 6, 16)
delivery_dt = date(2023, 6, 20)

hours = 0  # 0.7115
days_to_expiry = (expiry_dt - price_dt).days + hours/24
days_to_delivery = (delivery_dt - premium_dt).days + hours/24

r1_cont = np.log(1+ccy1*days_to_expiry/360)/(days_to_expiry/365)
r2_cont = np.log(1+ccy2*days_to_expiry/360)/(days_to_expiry/365)

delta = 0.25

# Compute strike from delta
k_25D = f*np.exp((1/2)*sigma**2*days_to_expiry/365 -
                 ppf(delta*np.exp(r1_cont*days_to_expiry/365))*sigma*np.sqrt(days_to_expiry/365))

# Get option value for computed strike and quoted strike
opt = [GK(f, strike, days_to_expiry, days_to_delivery, r1_cont, r2_cont, sigma)
       for strike in (k, k_25D)]

# Get spot premium
premium_dt_spot = date(2023, 3, 20)
days_to_delivery_spot = (delivery_dt - premium_dt_spot).days + hours/24
opt2 = [GK(f, strike, days_to_expiry, days_to_delivery_spot, r1_cont, r2_cont, sigma)
        for strike in (k, k_25D)]

Notional = 20_000_000

# Create first DataFrame
df = pd.DataFrame({
    "Strike": [k, k_25D],
    "Fwd Premium USD": [opt[0][0]*Notional, opt[1][0]*Notional],  # Fixed indexing
    "Spot Premium USD": [opt2[0][0]*Notional, opt2[1][0]*Notional],  # Fixed indexing
    "Fwd Delta": [opt[0][1]*100, opt[1][1]*100],  # Fixed indexing
    "Spot Delta": [opt[0][2]*100, opt[1][2]*100]  # Fixed indexing
})

# Create second DataFrame
df2 = pd.DataFrame({
    "Delta": [delta, opt[0][2]],  # Fixed indexing
    "Strike Solved": [k_25D, f*np.exp((1/2)*sigma**2*days_to_expiry/365 -
                     ppf(opt[0][2]*np.exp(r1_cont*days_to_expiry/365))*sigma*np.sqrt(days_to_expiry/365))]
})

print("\nMain Results:")
print(df)
print("\nDelta and Strike Solutions:")
print(df2)
# https://quant.stackexchange.com/questions/29507/calculate-strike-from-black-scholes-delta