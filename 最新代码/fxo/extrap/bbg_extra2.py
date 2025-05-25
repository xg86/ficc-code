import numpy as np
from scipy.interpolate import CubicSpline

# Given data
x = np.array([10, 25])
y = np.array([0.788, 0.353])

# Value to interpolate/extrapolate
x_new = 15

# Create the cubic spline interpolator with natural boundary conditions
cubic_spline = CubicSpline(x, y)

# Interpolate/extrapolate the value at x_new
y_new = cubic_spline(x_new)

print(f"Extrapolated value at x = {x_new}: {y_new:.3f}")
