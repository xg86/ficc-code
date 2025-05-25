import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

# Market data
deltas_put = [0.05, 0.10, 0.15, 0.25, 0.35]
vols_put = [5.185, 4.996, 4.929, 4.871, 4.788]  # In percentage

deltas_call = [0.05, 0.10, 0.15, 0.25, 0.35]  # Changed to increasing order
vols_call = [6.149, 5.784, 5.544, 5.224, 4.974]  # In percentage

# ATM point
atm_delta = 0.50
atm_vol = 4.770  # In percentage

# Create cubic spline interpolators with clamped boundary conditions
cs_put = CubicSpline(deltas_put + [atm_delta], vols_put + [atm_vol], bc_type=((1, 0), (1, 0)))
cs_call = CubicSpline(deltas_call + [atm_delta], vols_call + [atm_vol], bc_type=((1, 0), (1, 0)))

# Interpolate 15D and 35D points
delta_15 = 0.15
delta_35 = 0.35

vol_15_put = cs_put(delta_15)
vol_35_put = cs_put(delta_35)

vol_15_call = cs_call(delta_15)
vol_35_call = cs_call(delta_35)

# Extrapolate 5D points
delta_5 = 0.05
vol_5_put = cs_put(delta_5)
vol_5_call = cs_call(delta_5)

# Print results
print(f"5D Put Volatility: {vol_5_put:.3f}%")
print(f"15D Put Volatility: {vol_15_put:.3f}%")
print(f"35D Put Volatility: {vol_35_put:.3f}%")
print(f"5D Call Volatility: {vol_5_call:.3f}%")
print(f"15D Call Volatility: {vol_15_call:.3f}%")
print(f"35D Call Volatility: {vol_35_call:.3f}%")

# Plot the smile
deltas_plot = np.linspace(0.05, 0.50, 100)
vols_put_plot = cs_put(deltas_plot)
vols_call_plot = cs_call(deltas_plot)

plt.figure(figsize=(10, 6))
plt.plot(deltas_plot, vols_put_plot, label='Put Wing', color='blue')
plt.plot(deltas_plot, vols_call_plot, label='Call Wing', color='red')
plt.scatter(deltas_put + [atm_delta], vols_put + [atm_vol], color='blue', label='Put Market Data')
plt.scatter(deltas_call + [atm_delta], vols_call + [atm_vol], color='red', label='Call Market Data')
plt.title('FX Volatility Smile (Bloomberg-like Interpolation)')
plt.xlabel('Delta')
plt.ylabel('Implied Volatility (%)')
plt.legend()
plt.grid(True)
plt.show()