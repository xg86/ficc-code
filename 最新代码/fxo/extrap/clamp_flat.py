import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Sample data
x = np.array([0, 1, 2, 3, 4, 5])
y = np.array([0, 1, 4, 9, 16, 25])

# Define the interpolation function with clamped flat extrapolation
interp_func = interp1d(x, y, kind='linear', fill_value="extrapolate")

# Define the clamped flat extrapolation function
def clamped_flat_extrapolation(x_new):
    y_new = np.zeros_like(x_new)
    for i, xi in enumerate(x_new):
        if xi < x[0]:
            y_new[i] = y[0]
        elif xi > x[-1]:
            y_new[i] = y[-1]
        else:
            y_new[i] = interp_func(xi)
    return y_new

# New x values for interpolation and extrapolation
x_new = np.linspace(-2, 7, 100)
y_new = clamped_flat_extrapolation(x_new)

# Plot the results
plt.plot(x, y, 'o', label='Data points')
plt.plot(x_new, y_new, '-', label='Clamped flat extrapolation')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.title('Clamped Flat Extrapolation with SciPy')
plt.show()
