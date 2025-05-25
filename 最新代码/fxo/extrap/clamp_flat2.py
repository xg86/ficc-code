import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

# Example market data
market_strikes = np.array([1.20, 1.25, 1.30, 1.35, 1.40])
market_vols = np.array([0.18, 0.15, 0.16, 0.17, 0.20])

# Set boundary conditions for flat extrapolation
bc_type = ((1, 0.0), (1, 0.0))  # Derivative = 0 at both ends

# Fit cubic spline with clamped flat boundary conditions
#spline = CubicSpline(market_strikes, market_vols, bc_type='clamped', extrapolate=True)
spline = CubicSpline(market_strikes, market_vols, bc_type=bc_type)
# Evaluate spline and extrapolate
fit_strikes = np.linspace(1.10, 1.50, 100)  # Includes extrapolation range
fit_vols = spline(fit_strikes)

# Plot the results
plt.figure(figsize=(8, 5))
plt.plot(market_strikes, market_vols, 'o', label='Market Volatilities', color='red')
plt.plot(fit_strikes, fit_vols, label='Cubic Spline Fit', color='blue')
plt.axvline(x=1.20, linestyle='--', color='gray', alpha=0.6, label='Extrapolation Starts')
plt.axvline(x=1.40, linestyle='--', color='gray', alpha=0.6)
plt.title("Cubic Spline with Clamped Flat Extrapolation")
plt.xlabel("Strike")
plt.ylabel("Volatility")
plt.legend()
plt.grid()
plt.show()
