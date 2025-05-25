import numpy as np
from scipy.interpolate import interp1d

deltas_put = np.array([5, 10, 15, 20, 25, 30, 35, 40, 45])
deltas_call = np.array([45, 40, 35, 30, 25, 20, 15, 10, 5])
deltas_call_2 = np.array([49, 45, 40, 35, 30, 25, 20, 15, 10, 5, 1])

delta_matrix = {
    '1Y': {
        'call': {
            'strikes': np.array([6.962014287, 7.010784774, 7.06354245, 7.121943508, 7.188493448,7.269037941, 7.371298111, 7.515177416, 7.768648902]),
            'vols': np.array([0.052346, 0.053316, 0.054365, 0.055527, 0.056850, 0.058674, 0.060991, 0.064250, 0.069992])
        },
        'put': {
            'strikes': np.array([6.324865084, 6.460431249, 6.55030451,	6.620788133, 6.680576422, 6.732335933, 6.780615505, 6.826710927, 6.871571913]),
            'vols': np.array([0.054420,	0.053250,	0.052474,	0.051866,	0.051350,	0.051327, 0.051306, 0.051285, 0.051266])
        }
    },
    'ON': {
        'call': {
            'strikes': np.array([7.119878863,	7.121836142,	7.123898736,	7.126117283,	7.12856483,	7.131289497,	7.134520236,	7.138671576,	7.145008651]),
            'vols': np.array([0.040369,	0.040748,	0.041147,	0.041576,	0.042050,	0.042374,	0.042757,	0.043250,	0.044002])
        }
    },
    '1M': {
        'put': {
            'strikes':  np.array([6.851666033,	6.90909633,	6.947394513,	6.977573892,	7.003282354,	7.026349547,	7.04753629,	7.067473851,	7.08661017]),
            'vols': np.array([0.074688,0.073850,0.073291,	0.072850,	0.072475,	0.072022,	0.071605,	0.071213,	0.070837])
        }
    },
    '2M': {
        'call': {
            'strikes':  np.array([7.109282546,	7.132372064,	7.156795693,	7.183174412,	7.212410439,	7.245522141,	7.285249859,	7.337067678,	7.417923355]),
            'vols': np.array([0.059862,	0.060441,	0.061054,	0.061716,	0.062450,	0.063127,	0.063940,	0.065000,	0.066654])
        }
    },
    '4M': {
        'call': {
            'strikes': np.array([7.060646266, 7.083820186,	7.11404094,	7.146269871,	7.181388296,	7.220695936,
                                 7.266044354,	7.321376838, 7.395132665,	7.514048211,   7.775649402]),
            'vols': np.array([0.055919, 0.056488,	0.057229,	0.058019,	0.058880,	0.059843,
                              0.060890,	0.062167,	0.063870,	0.066615, 0.072653])
        }
    },
    '5M': {
        'call': {
            'strikes': np.array([7.041359148, 7.066926097,	7.100340663,	7.13606826,	7.175109892,	7.218948649,
                                 7.269535062,	7.331435018,	7.414257136, 7.548580724, 7.847863773]),
            'vols': np.array([0.054692, 0.055290,	0.056071,	0.056907,	0.057820, 0.058845,
                              0.059925,	0.061247,	0.063016,	0.065884, 0.072276])
        }
    },
    '60D': {
        'put': {
            'strikes': np.array(
                [6.791097005,	6.859233939,	6.90447599,	6.940014568,	6.970208918,	6.997264311,	7.022046758,	7.045308651,	7.06758125]),
            'vols': np.array([0.064506,	0.063560,	0.062932,	0.062438,	0.062019,	0.061525,	0.061072,	0.060647,	0.060241])
        }
    },
    '5D': {
        'call': {
            'strikes': np.array(
                [7.121560558,	7.125954188,	7.130596114,	7.135602767,	7.141142901,	7.147283202,	7.15456719,	7.163932043,	7.17823956]),
            'vols': np.array([0.040415,	0.040838,	0.041285,	0.041767,	0.042300,	0.042623,	0.043007,	0.043500,	0.044253])
        }
    },
    '6D': {
        'put': {
            'strikes': np.array(
                [6.993455155,	7.021457207,	7.040137323,	7.054862488,	7.067410391,	7.078721136,	7.089088548,	7.098826426,	7.108156598]),
            'vols': np.array([0.083231,	0.082500,	0.082012,	0.081628,	0.081300,	0.080774,	0.080292,	0.079840,	0.079406])
        }
    },
    '323D': {
        'call': {
            'strikes': np.array(
                [6.983344452,	7.029425043,	7.079141703,	7.134014927,	7.196334194,	7.271365147,	7.366072978,	7.498239888,	7.727796777]),
            'vols': np.array([0.052573,	0.053492,	0.054484,	0.055578,	0.056821,	0.058528,	0.060683,	0.063691,	0.068914])
        }
    },
    '218D': {
        'put': {
            'strikes': np.array(
                [6.511831751,	6.623952453,	6.698130553,	6.756230794,	6.805468824,	6.848572197,	6.888461244,	6.926262353,	6.962786813]),
            'vols': np.array([0.056822,	0.055655,	0.054882,	0.054277,	0.053764,	0.053556,	0.053364,	0.053182,	0.053007])
        }
    }
}

test_cases2 = np.array([
    [7.0495, "4M", "call"],
    [7.0291, "5M", "call"],
])

test_cases = np.array([
    [7.75, "1Y", "call"],
    [7.3, "1Y", "call"],
    [7.1, "1Y", "call"],
    [6.86, "1Y", "put"],
    [6.8, "1Y", "put"],
    #[7.0495, "4M", "call"],
    #[7.0291, "5M", "call"],
    #[6.95, "60D", "put"],  # 2024/12/30   6.9500p
    #[7.14, "5D", "call"],  # 2024/11/5  7.1400c
    #[7.11, "323D", "call"],  # 2025/9/19  7.1100c
    #[7.4, "2M", "call"],
    [7.14, "ON", "call"],
    [6.7, "218D", "put"],  # 2025/6/6 6.7000 p
    [6.97, "218D", "put"],  # 2025/6/6 6.97000 p
    [7.07, "6D", "put"]  # 2024/11/6  7.0700 p
])

def interpDeltaStrikes2(target_strike: float, tenor: str, optionType: str, kindMetheod: str= 'linear', interpMethod: str= 'extrapolate'):
    delta_strikes = delta_matrix[tenor][optionType]['strikes']
    delta_vols = delta_matrix[tenor][optionType]['vols']

    interpolator = interp1d(delta_strikes, delta_vols, kind=kindMetheod, fill_value=interpMethod)
    vol = interpolator(target_strike)

    interpolator_d = interp1d(delta_strikes, deltas_call_2, kind=kindMetheod, fill_value=interpMethod)
    delta = interpolator_d(target_strike)

    print(f"{optionType} Option at {tenor} with target_strike {target_strike}: Vol -> {vol:.6f}, delta -> {delta:.6f}")

# Use linear or cubic interpolation for delta-only IV curve
def interpDeltaStrikes(target_strike: float, tenor: str, optionType: str, kindMetheod: str= 'linear', interpMethod: str= 'extrapolate'):
    delta_strikes = delta_matrix[tenor][optionType]['strikes']
    delta_vols = delta_matrix[tenor][optionType]['vols']

    interpolator = interp1d(delta_strikes, delta_vols, kind=kindMetheod, fill_value=interpMethod)
    vol = interpolator(target_strike)

    deltas = deltas_put if optionType == 'put' else deltas_call
    interpolator_d = interp1d(delta_strikes, deltas, kind=kindMetheod, fill_value=interpMethod)
    delta = interpolator_d(target_strike)

    print(f"{optionType} Option at {tenor} with target_strike {target_strike}: Vol -> {vol:.6f}, delta -> {delta:.6f}")
    #interpolator_d = interp1d(delta_vols, deltas, kind='linear', fill_value="extrapolate")
    #delta = interpolator_d(iv)
    #print(f"IV for target_strike {target_strike}: {iv:.6f}, and delta {delta:.6f}")

for i in range(len(test_cases2)):
    interpDeltaStrikes2(test_cases2[i][0], test_cases2[i][1], test_cases2[i][2])

for i in range(len(test_cases)):
    interpDeltaStrikes(test_cases[i][0], test_cases[i][1], test_cases[i][2])

#1m 37.5d p
delta_vols_1m_put = delta_matrix['1M']['put']['vols']
delta_strikes_1m_put = delta_matrix['1M']['put']['strikes']
target_delta = 37.5
interpolator_delta_vol = interp1d(deltas_put, delta_vols_1m_put, kind='linear', fill_value="extrapolate")
vol = interpolator_delta_vol(target_delta)
interpolator_delta_strike = interp1d(deltas_put, delta_strikes_1m_put, kind='linear', fill_value="extrapolate")
strike = interpolator_delta_strike(target_delta)
#print(f"Implied Volatility for on 1m 37.5d p Delta {target_delta}: {implied_volatility:.6f}")
print(f"put Option at 1M with target_delta {target_delta}: Vol -> {vol:.6f}, strike -> {strike:.6f}")