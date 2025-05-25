import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d, CubicSpline
from numpy.polynomial.polynomial import Polynomial

# Sample data
#x = np.array([0, 1, 2, 3, 4])
#y = np.array([0, 1, 8, 27, 64])  # y = x^3 for this example

#x = np.array([10, 25, 50, 75, 90])
#y = np.array([   4.996,	4.871,	4.770,	5.224,	5.784])


x = np.array([10, 25, 50, 75, 90])
y = np.array([
    6.15,	5.95,	6,	6.65,	7.65
])
#not-a-knot
#natural
#clamped
# Create cubic interpolator
cubic_interp = CubicSpline(x, y,  bc_type='natural', extrapolate=True)
#cubic_interp = interp1d(x, y, kind='quadratic', fill_value="extrapolate", assume_sorted=True)


def cubic_interp_extrap(xval):
        return cubic_interp(xval)

# Test
#x_test = [15, 20, 30, 35, 40, 45, 55, 60, 65, 70, 80, 85]
#bbg_test = [15, 35, 65, 85]
#y_test = [cubic_interp_extrap(xi) for xi in bbg_test]

nj_test = [60, 70, 85, 15]
y_test = [cubic_interp_extrap(xi) for xi in nj_test]

print(f"Target y_test value: {y_test}")
# Plot
#plt.plot(x, y, 'o', label='Data Points')
#plt.plot(bbg_test, y_test, label='Cubic Interpolation/Extrapolation')
#plt.legend()
#plt.show()

