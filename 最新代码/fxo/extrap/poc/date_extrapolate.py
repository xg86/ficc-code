import numpy as np
from scipy.interpolate import interp1d

# Sample data: delta and implied volatility pairs
date = np.array([273, 365])
vols_10P = np.array([0.0628, 0.0643])
vols_25P = np.array([0.0568, 0.0569])
vols_50P = np.array([0.0520, 0.0513])
# Target delta for which we want to interpolate the IV

target_date= 323

# Use linear or cubic interpolation for delta-only IV curve
interpolator= interp1d(date, vols_10P, kind='linear', fill_value="extrapolate")
vol_10P = interpolator(target_date)
print(f"Implied Volatility for date {target_date}: {vol_10P:.6f}")

interpolator = interp1d(date, vols_25P, kind='linear', fill_value="extrapolate")
vol_25P = interpolator(target_date)
print(f"Implied Volatility for date {target_date}: {vol_25P:.6f}")

interpolator = interp1d(date, vols_50P, kind='linear', fill_value="extrapolate")
vol_50P = interpolator(target_date)
print(f"Implied Volatility for date {target_date}: {vol_50P:.6f}")

