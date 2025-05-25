import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
import matplotlib.pyplot as plt


# SABR model functions
def sabr_volatility(F, K, T, alpha, beta, rho, nu):
    """
    Calculate the implied volatility using the SABR model.
    """
    if K == F:
        K = F * 1.0001  # Avoid division by zero
    z = (nu / alpha) * (F * K) ** ((1 - beta) / 2) * np.log(F / K)
    x = np.log((np.sqrt(1 - 2 * rho * z + z ** 2) + z - rho) / (1 - rho))
    A = alpha / ((F * K) ** ((1 - beta) / 2) * (
                1 + ((1 - beta) ** 2 / 24) * np.log(F / K) ** 2 + ((1 - beta) ** 4 / 1920) * np.log(F / K) ** 4))
    B = 1 + (((1 - beta) ** 2 / 24) * (alpha ** 2 / (F * K) ** (1 - beta)) + (
                rho * beta * nu * alpha / (4 * (F * K) ** ((1 - beta) / 2))) + ((2 - 3 * rho ** 2) / 24) * nu ** 2) * T
    return A * (z / x) * B


def sabr_calibration(F, T, deltas, vols, beta=0.5):
    """
    Calibrate the SABR model parameters (alpha, rho, nu) to market data.
    """

    def objective(params):
        alpha, rho, nu = params
        errors = []
        for delta, vol in zip(deltas, vols):
            K = F * np.exp(-norm.ppf(delta) * vol * np.sqrt(T))  # Calculate strike
            sabr_vol = sabr_volatility(F, K, T, alpha, beta, rho, nu)
            errors.append(sabr_vol - vol)
        return np.sum(np.array(errors) ** 2)

    # Initial guess for alpha, rho, nu
    initial_guess = [0.2, 0.0, 0.2]
    bounds = [(0.01, 1.0), (-0.99, 0.99), (0.01, 1.0)]
    result = minimize(objective, initial_guess, bounds=bounds)
    if not result.success:
        raise ValueError("SABR calibration failed: " + result.message)
    return result.x


# Market data (10D, 25D, and ATM)
F = 1.2000  # Forward rate
T = 1.0  # Time to maturity (in years)

deltas_put = [0.10, 0.25]  # 10D and 25D puts
vols_put = [4.996, 4.871]  # In percentage

deltas_call = [0.25, 0.10]  # 25D and 10D calls
vols_call = [5.224, 5.784]  # In percentage

# ATM point
atm_delta = 0.50
atm_vol = 4.770  # In percentage

# Calibrate SABR model for puts and calls
try:
    alpha_put, rho_put, nu_put = sabr_calibration(F, T, deltas_put, vols_put)
    print("SABR parameters for puts:", alpha_put, rho_put, nu_put)
except ValueError as e:
    print("Error calibrating SABR for puts:", e)
    alpha_put, rho_put, nu_put = 0.2, 0.0, 0.2  # Fallback values

try:
    alpha_call, rho_call, nu_call = sabr_calibration(F, T, deltas_call, vols_call)
    print("SABR parameters for calls:", alpha_call, rho_call, nu_call)
except ValueError as e:
    print("Error calibrating SABR for calls:", e)
    alpha_call, rho_call, nu_call = 0.2, 0.0, 0.2  # Fallback values


# Calculate strikes for 5D, 15D, 35D
def calculate_strike(F, delta, vol, T, is_call=True):
    """
    Calculate the strike for a given delta using the Black-Scholes formula.
    """
    d1 = norm.ppf(delta if is_call else -delta)
    return F * np.exp(-d1 * vol * np.sqrt(T))


# Interpolate/extrapolate volatilities using the SABR model
delta_5 = 0.05
delta_15 = 0.15
delta_35 = 0.35

vol_5_put = sabr_volatility(F, calculate_strike(F, delta_5, atm_vol, T, is_call=False), T, alpha_put, 0.5, rho_put,
                            nu_put)
vol_15_put = sabr_volatility(F, calculate_strike(F, delta_15, atm_vol, T, is_call=False), T, alpha_put, 0.5, rho_put,
                             nu_put)
vol_35_put = sabr_volatility(F, calculate_strike(F, delta_35, atm_vol, T, is_call=False), T, alpha_put, 0.5, rho_put,
                             nu_put)

vol_5_call = sabr_volatility(F, calculate_strike(F, delta_5, atm_vol, T, is_call=True), T, alpha_call, 0.5, rho_call,
                             nu_call)
vol_15_call = sabr_volatility(F, calculate_strike(F, delta_15, atm_vol, T, is_call=True), T, alpha_call, 0.5, rho_call,
                              nu_call)
vol_35_call = sabr_volatility(F, calculate_strike(F, delta_35, atm_vol, T, is_call=True), T, alpha_call, 0.5, rho_call,
                              nu_call)

# Print results
print(f"5D Put Volatility: {vol_5_put:.3f}%")
print(f"15D Put Volatility: {vol_15_put:.3f}%")
print(f"35D Put Volatility: {vol_35_put:.3f}%")
print(f"5D Call Volatility: {vol_5_call:.3f}%")
print(f"15D Call Volatility: {vol_15_call:.3f}%")
print(f"35D Call Volatility: {vol_35_call:.3f}%")

# Plot the smile
deltas_plot = np.linspace(0.05, 0.50, 100)
vols_put_plot = [
    sabr_volatility(F, calculate_strike(F, delta, atm_vol, T, is_call=False), T, alpha_put, 0.5, rho_put, nu_put) for
    delta in deltas_plot]
vols_call_plot = [
    sabr_volatility(F, calculate_strike(F, delta, atm_vol, T, is_call=True), T, alpha_call, 0.5, rho_call, nu_call) for
    delta in deltas_plot]

plt.figure(figsize=(10, 6))
plt.plot(deltas_plot, vols_put_plot, label='Put Wing', color='blue')
plt.plot(deltas_plot, vols_call_plot, label='Call Wing', color='red')
plt.scatter(deltas_put, vols_put, color='blue', label='Put Market Data')
plt.scatter(deltas_call, vols_call, color='red', label='Call Market Data')
plt.title('FX Volatility Smile (SABR Model)')
plt.xlabel('Delta')
plt.ylabel('Implied Volatility (%)')
plt.legend()
plt.grid(True)
plt.show()