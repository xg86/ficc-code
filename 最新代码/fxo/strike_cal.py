import numpy as np
from scipy.stats import norm
from scipy.optimize import root_scalar

# Given parameters
S = 7.12000          # Spot price
#r_d = 0.02          # Domestic interest rate
#r_f = 0.01          # Foreign interest rate
r_d = 0.0192927  # CNY
r_f = 0.0503185  # USD
sigma = 0.05685         # Implied volatility
T = 1             # Time to maturity in years
target_delta = 0.25 # Target delta for the call (e.g., 25-delta call)

# Define the delta function for a call option
def delta_call_strike(K):
    d1 = (np.log(S / K) + (r_d - r_f + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    delta_call = np.exp(-r_f * T) * norm.cdf(d1)
    return delta_call - target_delta

# Find the strike that gives the target delta
result = root_scalar(delta_call_strike, bracket=[S * 0.5, S * 1.5], method='bisect')
if result.converged:
    strike_for_target_delta = result.root
    print(f"The strike price for a {target_delta * 100:.0f}-delta call is: {strike_for_target_delta:.4f}")
else:
    print("Could not find a strike for the target delta.")
