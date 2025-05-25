import numpy as np
from scipy.interpolate import interp2d

import warnings
warnings.filterwarnings("ignore")

# Example data: delta, strike, and IV surface grid
#deltas = np.array([0.1, 0.25, 0.5, 0.75, 0.9])    # Example delta points
deltas = np.array([5, 10, 15, 20,
                   25, 30, 35, 40, 45])
strikes_1y_call = np.array([6.962014287, 7.010784774, 7.06354245, 7.121943508,
                            7.188493448, 7.269037941, 7.371298111, 7.515177416, 7.768648902]) # Example strike prices

iv_surface_call = np.array([                           # IV values at each delta-strike point
    [
0.076698,
0.071835,
0.066654,
0.068021,
0.066615,
0.065884,
0.065489,
0.067244,
0.069992],               # IV at delta = 5
    [
0.075350,
0.070342,
0.065000,
0.065500,
0.063870,
0.063016,
0.062550,
0.062800,
0.064250],               # IV at delta = 10
    [

0.074474,
0.069377,
0.063940,
0.063922,
0.062167,
0.061247,
0.060744,
0.060187,
0.060991],               # IV at delta = 15
    [
0.073795,
0.068634,
0.063127,
0.062731,
0.060890,
0.059925,
0.059398,
0.058291,
0.058674],               # IV at delta = 20
    [
0.073225,
0.068011,
0.062450,
0.061750,
0.059843,
0.058845,
0.058300,
0.056775,
0.056850] ,               # IV at delta =  25
    [
0.072606,
0.067394,
0.061716,
0.060885,
0.058880,
0.057820,
0.057238,
0.055658,
0.055527],# IV at delta =  30
    [
0.072044,
0.066835,
0.061054,
0.060108,
0.058019,
0.056907,
0.056295,
0.054670,
0.054365],    # IV at delta =  35
    [
0.071520,
0.066314,
0.060441,
0.059391,
0.057229,
0.056071,
0.055433,
0.053770,
0.053316],    # IV at delta =  40
    [
0.071022,
0.065819,
0.059862,
0.058717,
0.056488,
0.055290,
0.054628,
0.052933,
0.052346]    # IV at delta =  45
])
implied_vols_1y_call = np.array([0.052346, 0.053316, 0.054365, 0.055527, 0.056850, 0.058674, 0.060991, 0.064250, 0.069992])

# Target delta and strike
target_delta = 0.3
target_strike = 7.75

# Interpolating IV for target delta and strike
interpolator = interp2d(strikes_1y_call, deltas, iv_surface_call, kind='linear')
implied_volatility = interpolator(target_strike, target_delta)[0]

print(f"Implied Volatility for Delta {target_delta} and Strike {target_strike}: {implied_volatility:.6f}")