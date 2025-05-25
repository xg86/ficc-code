import QuantLib as ql
import numpy as np

# Current date
today = ql.Date(15, ql.November, 2023)
ql.Settings.instance().evaluationDate = today

# Market data
strikes = [90, 95, 100, 105, 110]
implied_vols = [0.25, 0.24, 0.23, 0.24, 0.26]  # Market implied volatilities
expiry_date = ql.Date(15, ql.March, 2024)

# Create log-moneyness
spot_price = 100
forward_price = spot_price  # Assume no carry costs for simplicity
log_moneyness = [np.log(K / forward_price) for K in strikes]

# Initialize SVI parameters
a, b, rho, m, sigma = 0.04, 0.1, -0.3, 0.0, 0.1  # Initial guesses for SVI parameters

# Define SVI formula
def svi_formula(k, a, b, rho, m, sigma):
    return a + b * (rho * (k - m) + np.sqrt((k - m)**2 + sigma**2))

# Objective function for parameter calibration
def svi_loss(params, log_m, market_vols):
    a, b, rho, m, sigma = params
    model_vols = [np.sqrt(svi_formula(k, a, b, rho, m, sigma)) for k in log_m]
    return np.sum((np.array(model_vols) - np.array(market_vols))**2)

# Calibrate SVI parameters using scipy.optimize
from scipy.optimize import minimize

initial_params = [a, b, rho, m, sigma]
bounds = [(0, None), (0, None), (-1, 1), (None, None), (0, None)]  # Ensure valid parameter ranges

result = minimize(
    svi_loss, initial_params, args=(log_moneyness, implied_vols), bounds=bounds
)

# Extract calibrated parameters
a, b, rho, m, sigma = result.x
print("Calibrated SVI Parameters:")
print(f"a = {a:.6f}, b = {b:.6f}, rho = {rho:.6f}, m = {m:.6f}, sigma = {sigma:.6f}")

# Plotting the calibrated SVI curve
import matplotlib.pyplot as plt

log_m_interp = np.linspace(min(log_moneyness), max(log_moneyness), 100)
vol_interp = [np.sqrt(svi_formula(k, a, b, rho, m, sigma)) for k in log_m_interp]

plt.figure(figsize=(8, 5))
plt.scatter(log_moneyness, implied_vols, color="red", label="Market Data")
plt.plot(log_m_interp, vol_interp, label="SVI Fit", color="blue")
plt.title("SVI Calibration and Fit")
plt.xlabel("Log-Moneyness")
plt.ylabel("Implied Volatility")
plt.legend()
plt.grid()
plt.show()
