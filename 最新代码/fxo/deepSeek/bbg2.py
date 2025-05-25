import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

# Bloomberg input data (10D, 25D, and ATM)
deltas_put = [0.10, 0.25]  # 10D and 25D puts
vols_put = [4.996, 4.871]  # In percentage

deltas_call = [0.10, 0.25]  # 10D and 25D calls
vols_call = [5.784, 5.224]  # In percentage

# ATM point
atm_delta = 0.50
atm_vol = 4.770  # In percentage

# Print input data for verification
print("Put Deltas:", deltas_put)
print("Put Vols:", vols_put)
print("Call Deltas:", deltas_call)
print("Call Vols:", vols_call)
print("ATM Delta:", atm_delta)
print("ATM Vol:", atm_vol)

# Create cubic spline interpolators with clamped boundary conditions
# For puts: Use 10D, 25D, and ATM
cs_put = CubicSpline(deltas_put + [atm_delta], vols_put + [atm_vol], bc_type=((1, 0), (1, 0)))

# For calls: Use 10D, 25D, and ATM (in increasing order)
# Reverse the order of deltas_call and vols_call to ensure increasing order
cs_call = CubicSpline([0.10, 0.25, 0.50], [5.784, 5.224, 4.770], bc_type=((1, 0), (1, 0)))

# Print cubic spline results for verification
print("Cubic Spline for Puts:", cs_put)
print("Cubic Spline for Calls:", cs_call)

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
plt.scatter([0.10, 0.25, 0.50], [5.784, 5.224, 4.770], color='red', label='Call Market Data')
plt.title('FX Volatility Smile (Interpolated from 10D, 25D, and ATM)')
plt.xlabel('Delta')
plt.ylabel('Implied Volatility (%)')
plt.legend()
plt.grid(True)
plt.show()