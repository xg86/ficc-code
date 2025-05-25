import QuantLib as ql
import numpy as np

# Define market data: strikes, expiries, and market volatilities
strikes = [80, 90, 100, 110, 120]
expiries = [ql.Period(1, ql.Months), ql.Period(3, ql.Months), ql.Period(6, ql.Months), ql.Period(1, ql.Years)]
market_vols = [
    [0.35, 0.30, 0.25, 0.20, 0.18],  # 1 month
    [0.34, 0.29, 0.24, 0.19, 0.17],  # 3 months
    [0.33, 0.28, 0.23, 0.18, 0.16],  # 6 months
    [0.32, 0.27, 0.22, 0.17, 0.15]  # 1 year
]

# Create QuantLib objects
calendar = ql.TARGET()
settlement_date = ql.Date(15, ql.August, 2023)
ql.Settings.instance().evaluationDate = settlement_date

# Create the SABR model
sabr_params = [0.04, 0.5, 0.2, 0.0]  # initial guess for alpha, beta, nu, rho

# Create a SABR interpolation for each expiry
vols_interpolations = []
for i, expiry in enumerate(expiries):
    expiry_date = settlement_date + expiry
    times = ql.Actual365Fixed().yearFraction(settlement_date, expiry_date)
    sabr_interpolation = ql.SabrSmileSection(
        settlement_date,
        1.1, #fwd
        sabr_params,
        settlement_date,
        ql.Actual365Fixed(),
        0.0,
        ql.ShiftedLognormal)
    vols_interpolations.append(sabr_interpolation)

# Example: Retrieve SABR implied volatility for a specific strike and expiry
strike = 105
expiry_index = 2  # 6 months
implied_vol = vols_interpolations[expiry_index].volatility(strike)
print(f"SABR Implied volatility for strike {strike} and 6 months expiry: {implied_vol:.4f}")

# Plot the SABR volatility surface
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

strike_grid = np.linspace(80, 120, 50)
time_grid = np.array(
    [ql.Actual365Fixed().yearFraction(settlement_date, settlement_date + expiry) for expiry in expiries])

X, Y = np.meshgrid(strike_grid, time_grid)
Z = np.array([[vols_interpolations[j].volatility(strike) for strike in strike_grid] for j in range(len(expiries))])

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis')

ax.set_xlabel('Strike')
ax.set_ylabel('Time to Maturity')
ax.set_zlabel('Implied Volatility')
plt.show()