import QuantLib as ql
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Today's date and evaluation settings
today = ql.Date(29, ql.November, 2023)
ql.Settings.instance().evaluationDate = today

# Market data: Volatility by delta (25D, 50D)
deltas = [0.25, 0.50, 0.75]  # Delta levels
vols = [0.26, 0.23, 0.24]  # Corresponding volatilities
expiry_date = ql.Date(29, ql.March, 2024)  # Expiry date

# Additional parameters
spot_price = 100.0  # Spot price
risk_free_rate = 0.01  # Risk-free rate
dividend_yield = 0.0  # No dividends assumed
time_to_expiry = ql.Actual365Fixed().yearFraction(today, expiry_date)


# Black-Scholes model to compute strikes from deltas
def delta_to_strike(delta, vol, spot, t, r, is_call=True):
    """Convert delta to strike using the Black-Scholes formula."""
    from scipy.stats import norm

    sign = 1 if is_call else -1
    d1 = lambda k: (np.log(spot / k) + (r + (vol ** 2) / 2) * t) / (vol * np.sqrt(t))
    strike_func = lambda k: norm.cdf(sign * d1(k)) - delta
    # Use numerical root-finding to solve for strike
    from scipy.optimize import brentq
    return brentq(strike_func, 0.1 * spot, 2.0 * spot)


# Calculate strikes from deltas
strikes = [
    delta_to_strike(delta, vol, spot_price, time_to_expiry, risk_free_rate, is_call=(delta >= 0.5))
    for delta, vol in zip(deltas, vols)
]

# Log-moneyness calculation
forward_price = spot_price * np.exp((risk_free_rate - dividend_yield) * time_to_expiry)
log_moneyness = [np.log(k / forward_price) for k in strikes]

# Initialize SVI parameters
a, b, rho, m, sigma = 0.04, 0.1, -0.3, 0.0, 0.1  # Initial guesses


# Define SVI formula
def svi_formula(k, a, b, rho, m, sigma):
    return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + sigma ** 2))


# Objective function for parameter calibration
def svi_loss(params, log_m, market_vols):
    a, b, rho, m, sigma = params
    model_vols = [np.sqrt(svi_formula(k, a, b, rho, m, sigma)) for k in log_m]
    return np.sum((np.array(model_vols) - np.array(market_vols)) ** 2)


# Calibrate SVI parameters using scipy.optimize
initial_params = [a, b, rho, m, sigma]
bounds = [(0, None), (0, None), (-1, 1), (None, None), (0, None)]  # Valid parameter ranges

result = minimize(
    svi_loss, initial_params, args=(log_moneyness, vols), bounds=bounds
)

# Extract calibrated parameters
a, b, rho, m, sigma = result.x
print("Calibrated SVI Parameters:")
print(f"a = {a:.6f}, b = {b:.6f}, rho = {rho:.6f}, m = {m:.6f}, sigma = {sigma:.6f}")

# Compute deltas for interpolated log-moneyness
log_m_interp = np.linspace(min(log_moneyness), max(log_moneyness), 100)
vol_interp = [np.sqrt(svi_formula(k, a, b, rho, m, sigma)) for k in log_m_interp]


# Function to calculate delta from strike (reverse process)
def strike_to_delta(strike, vol, spot, t, r, is_call=True):
    """Convert strike to delta using the Black-Scholes formula."""
    from scipy.stats import norm

    d1 = (np.log(spot / strike) + (r + (vol ** 2) / 2) * t) / (vol * np.sqrt(t))
    delta = norm.cdf(d1) if is_call else norm.cdf(d1) - 1
    return delta


# Compute deltas for interpolated points
interp_deltas = [
    strike_to_delta(forward_price * np.exp(k), np.sqrt(svi_formula(k, a, b, rho, m, sigma)),
                    spot_price, time_to_expiry, risk_free_rate, is_call=(k >= 0))
    for k in log_m_interp
]

# Compute deltas for market data (for plotting)
market_deltas = [
    strike_to_delta(strike, vol, spot_price, time_to_expiry, risk_free_rate, is_call=(delta >= 0.5))
    for strike, vol, delta in zip(strikes, vols, deltas)
]

# Plotting: Delta on X-Axis
plt.figure(figsize=(8, 5))
plt.scatter(market_deltas, vols, color="red", label="Market Data (Vol/Delta)")
plt.plot(interp_deltas, vol_interp, label="SVI Fit", color="blue")
plt.title("SVI Calibration with Delta on X-Axis")
plt.xlabel("Delta")
plt.ylabel("Implied Volatility")
plt.legend()
plt.grid()
plt.show()
