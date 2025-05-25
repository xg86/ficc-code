import numpy as np
from scipy.interpolate import interp1d

# Sample data: delta and implied volatility pairs
strikes_1y_call = np.array([6.962014287,	7.010784774, 7.06354245, 7.121943508, 7.188493448,7.269037941, 7.371298111, 7.515177416, 7.768648902])
implied_vols_1y_call = np.array([0.052346, 0.053316, 0.054365, 0.055527, 0.056850, 0.058674, 0.060991, 0.064250, 0.069992])

# Target delta for which we want to interpolate the IV
target_strike_1 = 7.75
target_strike_2 = 7.3
target_strike_3 = 7.1


# Use linear or cubic interpolation for delta-only IV curve
#interpolator_1y_call = interp1d(strikes_1y_call, implied_vols_1y_call, kind='linear', fill_value="extrapolate")
#implied_volatility = interpolator_1y_call(target_strike_1)

#print(f"Implied Volatility for 1y 7.7500c Delta {target_strike_1}: {implied_volatility:.6f}")
#implied_volatility = interpolator_1y_call(target_strike_2)
#print(f"Implied Volatility for 1y 7.3000c Delta {target_strike_2}: {implied_volatility:.6f}")
#implied_volatility = interpolator_1y_call(target_strike_3)
#print(f"Implied Volatility for 1y 7.1000c Delta {target_strike_3}: {implied_volatility:.6f}")

strikes_1y_put = np.array([6.324865084,	6.460431249,	6.55030451,	6.620788133,	6.680576422,	6.732335933,	6.780615505,	6.826710927,	6.871571913])
implied_vols_1y_put = np.array([0.054420,	0.053250,	0.052474,	0.051866,	0.051350,	0.051327,	0.051306,	0.051285,	0.051266])

target_strike_4 = 6.86
target_strike_5 = 6.8


interpolator_1y_put = interp1d(strikes_1y_put, implied_vols_1y_put, kind='linear', fill_value="extrapolate")
implied_volatility = interpolator_1y_put(target_strike_4)
print(f"Implied Volatility for 1y 6.8600p Delta {target_strike_4}: {implied_volatility:.6f}")
implied_volatility = interpolator_1y_put(target_strike_5)
print(f"Implied Volatility for 1y 6.8000p Delta {target_strike_5}: {implied_volatility:.6f}")

strikes_4m_call = np.array([7.083820186,	7.11404094,	7.146269871,	7.181388296,	7.220695936,	7.266044354,	7.321376838,	7.395132665,	7.514048211])
implied_vols_4m_call = np.array([0.056488,	0.057229,	0.058019,	0.058880,	0.059843,	0.060890,	0.062167,	0.063870,	0.066615])
target_strike_6 = 7.0495

interpolator_4m_call = interp1d(strikes_4m_call, implied_vols_4m_call, kind='linear', fill_value="extrapolate")
implied_volatility = interpolator_4m_call(target_strike_6)
print(f"Implied Volatility for 4m 7.0495c Delta {target_strike_6}: {implied_volatility:.6f}")

strikes_5m_call = np.array([7.066926097,	7.100340663,	7.13606826,	7.175109892,	7.218948649,	7.269535062,	7.331435018,	7.414257136,	7.548580724])
implied_vols_5m_call = np.array([0.055290,	0.056071,	0.056907,	0.057820,	0.058845,	0.059925,	0.061247,	0.063016,	0.065884])
target_strike_7 = 7.0291
interpolator_5m_call = interp1d(strikes_5m_call, implied_vols_5m_call, kind='linear', fill_value="extrapolate")
implied_volatility = interpolator_5m_call(target_strike_7)
print(f"Implied Volatility for 5m 7.0291c Delta {target_strike_7}: {implied_volatility:.6f}")

strikes_2m_call = np.array([7.109282546,	7.132372064,	7.156795693,	7.183174412,	7.212410439,	7.245522141,	7.285249859,	7.337067678,	7.417923355])
implied_vols_2m_call = np.array([0.059862,	0.060441,	0.061054,	0.061716,	0.062450,	0.063127,	0.063940,	0.065000,	0.066654])
target_strike_11 = 7.4
interpolator_2m_call = interp1d(strikes_2m_call, implied_vols_2m_call, kind='linear', fill_value="extrapolate")
implied_volatility = interpolator_2m_call(target_strike_11)
print(f"Implied Volatility for 2m 7.4000c Delta {target_strike_11}: {implied_volatility:.6f}")

strikes_on_call = np.array([7.119878863,	7.121836142,	7.123898736,	7.126117283,	7.12856483,	7.131289497,	7.134520236,	7.138671576,	7.145008651])
implied_vols_on_call = np.array([0.040369,	0.040748,	0.041147,	0.041576,	0.042050,	0.042374,	0.042757,	0.043250,	0.044002])
target_strike_12 = 7.14

interpolator_on_call = interp1d(strikes_on_call, implied_vols_on_call, kind='linear', fill_value="extrapolate")
implied_volatility = interpolator_on_call(target_strike_12)
print(f"Implied Volatility for on 7.1400c Delta {target_strike_12}: {implied_volatility:.6f}")

delta_1m = np.array([5,10,15,	20,	25,30,	35,	40,45])
implied_vols_1m_put = np.array([0.074688,0.073850,0.073291,	0.072850,	0.072475,	0.072022,	0.071605,	0.071213,	0.070837])
target_strike_15 = 37.5
interpolator_delta_1m_put = interp1d(delta_1m, implied_vols_1m_put, kind='linear', fill_value="extrapolate")
implied_volatility = interpolator_delta_1m_put(target_strike_15)
print(f"Implied Volatility for on 1m 37.5d p Delta {target_strike_15}: {implied_volatility:.6f}")