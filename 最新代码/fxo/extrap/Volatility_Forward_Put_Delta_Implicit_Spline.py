#Volatility vs. Forward Put Delta (Implicit Spline)
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# Input Data: Forward Put Delta and Implied Volatility
# Example input data, replace these with your actual market data
#put_deltas = np.array([-0.25, -0.20, -0.15, -0.10, -0.05])  # Put deltas (negative for puts)
#implied_vols = np.array([0.24, 0.22, 0.20, 0.21, 0.25])      # Corresponding implied volatilities
#put_deltas = np.array([-0.90, -0.75, -0.50, -0.25, -0.10])
#implied_vols = np.array([5.784, 5.224, 4.77,  4.871, 4.996])
put_deltas = np.array([-0.90, -0.75, -0.50, -0.25, -0.10])
implied_vols = np.array([4.996, 4.871, 4.77,  5.224, 5.784])

# Step 1: Ensure Monotonicity by Sorting Delta and Corresponding Volatilities
sorted_indices = np.argsort(put_deltas)
sorted_deltas = put_deltas[sorted_indices]
sorted_vols = implied_vols[sorted_indices]

# Step 2: Calculate Clamped Derivatives for Boundary Conditions
# Forward difference for the left boundary, backward difference for the right boundary
left_slope = (sorted_vols[1] - sorted_vols[0]) / (sorted_deltas[1] - sorted_deltas[0])
right_slope = (sorted_vols[-1] - sorted_vols[-2]) / (sorted_deltas[-1] - sorted_deltas[-2])

# Step 3: Interpolate Using Implicit (Clamped) Cubic Spline
spline = CubicSpline(sorted_deltas, sorted_vols,
                     bc_type=((1, left_slope), (1, right_slope)))

# Step 4: Create a Finer Grid for Smooth Plotting
fine_deltas = np.linspace(min(sorted_deltas) - 0.05, max(sorted_deltas) + 0.05, 100)
fine_vols = spline(fine_deltas)

implied_vols_spline = spline(sorted_deltas)
print(implied_vols_spline)

put_deltas_interp = np.array([-0.90, -0.85, -0.75, -0.65, -0.50, -0.35, -0.25, -0.15, -0.10])

implied_vols_spline_interp = spline(put_deltas_interp)
print(implied_vols_spline_interp)

# Step 5: Extrapolate Linearly for Points Outside Known Data Range
def linear_extrapolation(x, y, target_x):
    # Use the last two points for slope calculation (right extrapolation)
    if target_x > x[-1]:
        slope = (y[-1] - y[-2]) / (x[-1] - x[-2])
        return y[-1] + slope * (target_x - x[-1])
    # Use the first two points for slope calculation (left extrapolation)
    elif target_x < x[0]:
        slope = (y[1] - y[0]) / (x[1] - x[0])
        return y[0] + slope * (target_x - x[0])
    else:
        return None  # No extrapolation needed

# Apply Linear Extrapolation Outside the Data Range
extrapolated_vols = [
    linear_extrapolation(sorted_deltas, sorted_vols, delta) if (delta < sorted_deltas[0] or delta > sorted_deltas[-1]) else vol
    for delta, vol in zip(fine_deltas, fine_vols)
]
print(fine_deltas)
print(extrapolated_vols)

# Step 6: Plot the Volatility Smile
plt.figure(figsize=(10, 6))
plt.plot(fine_deltas, extrapolated_vols, label='Volatility vs. Put Delta (Implicit Spline)', color='blue')
plt.scatter(sorted_deltas, sorted_vols, color='red', label='Market Data Points')
plt.title('Volatility vs. Forward Put Delta - Implicit Clamped Cubic Spline')
plt.xlabel('Forward Put Delta')
plt.ylabel('Implied Volatility')
plt.legend()
plt.grid(True)
plt.show()
