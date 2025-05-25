def interpolate_implied_vol(delta, v_atm, rr_25, str_25, delta_atm=0.5):
    """
    Interpolates the implied volatility for a given delta using ATM volatility,
    25-delta risk reversal, and 25-delta strangle.

    Parameters:
    delta (float): The target delta (e.g., 0.375 for 37.5-delta).
    v_atm (float): The ATM volatility.
    rr_25 (float): The 25-delta risk reversal.
    str_25 (float): The 25-delta strangle (smile adjustment).
    delta_atm (float): The ATM delta, default is 0.5.

    Returns:
    float: Interpolated implied volatility for the target delta.
    """
    # Calculate the difference from ATM delta
    delta_diff = delta - delta_atm

    # Apply the interpolation formula
    v_delta = v_atm - 2 * rr_25 * delta_diff + 16 * str_25 * delta_diff ** 2
    return v_delta


# Example usage
v_atm = 0.10  # ATM volatility (10%)
rr_25 = 0.02  # 25-delta risk reversal (2%)
str_25 = 0.015  # 25-delta strangle (1.5%)
delta_call = 0.375  # Target delta (37.5-delta)
delta_put = -0.375  # Target delta (37.5-delta)
# Calculate the interpolated volatility for the target delta
v_interpolated = interpolate_implied_vol(delta_call, v_atm, rr_25, str_25)
print(f"delta_call volatility for {delta_call * 100:.1f}-delta: {v_interpolated:.4f}")


v_interpolated = interpolate_implied_vol(delta_put, v_atm, rr_25, str_25)
print(f"delta_put volatility for {delta_put * 100:.1f}-delta: {v_interpolated:.4f}")


v_atm_1m = (4.71+5.31)/2/100  # ATM volatility (10%)
rr_25_1m = (-0.442+0.158)/2/100 # 25-delta risk reversal (2%)
bf_25_1m = (0.130+0.230)/2/100
rr_10_1m = (-0.617-0.017)/2/100 # 25-delta risk reversal (2%)
bf_10_1m = (0.247+0.447)/2/100


vol_25_call = v_atm_1m+0.5*rr_25_1m+bf_25_1m
vol_25_put = v_atm_1m-0.5*rr_25_1m+bf_25_1m
vol_10_call = v_atm_1m+0.5*rr_10_1m+bf_10_1m
vol_10_put = v_atm_1m-0.5*rr_10_1m+bf_10_1m

print(f"vol_25_call: {vol_25_call:.4f}")
print(f"vol_10_call: {vol_10_call:.4f}")
print(f"v_atm_1m : {v_atm_1m:.4f}")
print(f"vol_10_put : {vol_10_put:.4f}")
print(f"vol_25_put : {vol_25_put:.4f}")




delta_call_35 = 0.35  # put Target delta (37.5-delta)
delta_put_35 = -0.35  # put Target delta (37.5-delta)

str_25_1m = (v_atm_1m + bf_25_1m)
#print(f"str_25_1m with v_atm_1m and bf_25_1m : {str_25_1m:.4f}")
v_35_call_1m = interpolate_implied_vol(delta_call_35, v_atm_1m, rr_25_1m, str_25_1m*0.05)
#print(f"call Interpolated volatility for {delta_1m_call * 100:.1f}-delta: {v_35_call_1m:.4f}")


v_35_put_1m = interpolate_implied_vol(delta_put_35, v_atm_1m, rr_25_1m, str_25_1m*0.05)
#print(f"call Interpolated volatility for {delta_1m_put * 100:.1f}-delta: {v_35_put_1m:.4f}")

import numpy as np
from scipy.interpolate import interp1d

deltas = np.array([10, 25, 50, 75, 90])
implied_vols_1m = np.array([ vol_10_call, vol_25_call, v_atm_1m, vol_10_put, vol_25_put])

interpolator= interp1d(deltas, implied_vols_1m, kind='linear', fill_value="extrapolate")
vol_35 = interpolator(35)
vol_65 = interpolator(65)
print(f"extrapolate linear vol_35: {vol_35:.6f}")
print(f"extrapolate linear vol_65: {vol_65:.6f}")


v_atm_1y = (4.7	+	5.1)/2/100  # ATM volatility (10%)
rr_25_1y = (0.317	+	0.717)/2/100# 25-delta risk reversal (2%)
bf_25_1y = (0.204	+	0.354)/2/100
rr_10_1y = (1.075	+	1.475)/2/100 # 25-delta risk reversal (2%)
bf_10_1y = (0.661	+	0.861)/2/100


vol_25_call_1y = v_atm_1y+0.5*rr_25_1y+bf_25_1y
vol_25_put_1y = v_atm_1y-0.5*rr_25_1y+bf_25_1y
vol_10_call_1y = v_atm_1y+0.5*rr_10_1y+bf_10_1y
vol_10_put_1y = v_atm_1y-0.5*rr_10_1y+bf_10_1y

print(f"vol_25_call_1y: {vol_25_call_1y:.6f}")
print(f"vol_10_call_1y: {vol_10_call_1y:.6f}")
print(f"v_atm_1y : {v_atm_1y:.4f}")
print(f"vol_10_put_1y : {vol_10_put_1y:.6f}")
print(f"vol_25_put_1y : {vol_25_put_1y:.6f}")

str_25_1y = (vol_25_call_1y + vol_25_put_1y)/2-v_atm_1y
print(f"str_25_1y : {str_25_1y:.6f}")
#str_25_1y = (v_atm_1y + bf_25_1y)
#print(f"str_25_1y : {str_25_1y:.6f}")

v_35_call_1y = interpolate_implied_vol(delta_call_35, v_atm_1y, rr_25_1y, str_25_1y)
print(f"v_35_call_1y : {v_35_call_1y:.6f}")

v_35_put_1y = interpolate_implied_vol(delta_put_35, v_atm_1y, rr_25_1y, str_25_1y)
print(f"v_35_put_1y : {v_35_put_1y:.6f}")