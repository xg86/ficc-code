import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d, CubicSpline
from numpy.polynomial.polynomial import Polynomial

# Sample data
#x = np.array([0, 1, 2, 3, 4])
#y = np.array([0, 1, 8, 27, 64])  # y = x^3 for this example

x = np.array([10, 25, 75, 90])
y = np.array([0.788, 0.353, 0.2775, 0.62])
#y = np.array([0.62, 0.2775, 0.353, 0.788])
# Create cubic interpolator
# cubic_interp = interp1d(x, y, kind='cubic', fill_value="extraplate")
cubic_interp = CubicSpline(x, y, bc_type='natural', extrapolate=True)
y_new = cubic_interp(5)
print(f"Target 5 value: {y_new:.6f}")
y_new = cubic_interp(15)
print(f"Target 15 value: {y_new:.6f}")
y_new = cubic_interp(35)
print(f"Target 35 value: {y_new:.6f}")
y_new = cubic_interp(65)
print(f"Target 65 value: {y_new:.6f}")
y_new = cubic_interp(85)
print(f"Target 85 value: {y_new:.6f}")
y_new = cubic_interp(95)
print(f"Target 95 value: {y_new:.6f}")

# Fit cubic polynomials for extrapolation
# Fit to the first three and last three points
coeffs_left = Polynomial.fit(x[:4], y[:4], deg=2).convert().coef
coeffs_right = Polynomial.fit(x[-4:], y[-4:], deg=2).convert().coef

# Define the cubic extrapolators
def cubic_extrapolate_left(xval):
    return coeffs_left[0] + coeffs_left[1] * xval + coeffs_left[2] * xval**2

def cubic_extrapolate_right(xval):
    return coeffs_right[0] + coeffs_right[1] * xval + coeffs_right[2] * xval**2

# Combined interpolator and extrapolator
def cubic_interp_extrap(xval):
    if xval < x[0]:
        return cubic_extrapolate_left(xval)
    elif xval > x[-1]:
        return cubic_extrapolate_right(xval)
    else:
        return cubic_interp(xval)
    '''
    elif xval > 25 and xval < 50:
        return cubic_extrapolate_right(xval)
    elif xval > 50 and xval < 75:
        return cubic_extrapolate_left(xval)
    '''


# Test
x_test = [5, 15, 35, 65, 85,95]
y_test = [cubic_interp_extrap(xi) for xi in x_test]
print(f"Target y_test value: {y_test}")
# Plot
plt.plot(x, y, 'o', label='Data Points')
plt.plot(x_test, y_test, label='Cubic Interpolation/Extrapolation')
plt.legend()
plt.show()

