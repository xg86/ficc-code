import numpy as np
from scipy.interpolate import interp1d

deltas_put = np.array([5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
deltas_call = deltas_put
#deltas_call = np.array([45, 40, 35, 30, 25, 20, 15, 10, 5])
deltas_call_2 = np.array([49, 45, 40, 35, 30, 25, 20, 15, 10, 5, 1])

delta_matrix = {
    '1Y': {
        'call': {
            'strikes': np.array([7.7076300237197035, 7.49645934429669, 7.358144228170767, 7.252957388585654, 7.167557866881379, 7.100789105979511, 7.04118228083984, 6.986808751834268, 6.936317344282487, 6.888670591301105]),
            'vols': np.array([0.06671666666666667, 0.06425, 0.061783333333333336, 0.05931666666666666, 0.05685, 0.055729999999999995, 0.05461, 0.053489999999999996, 0.05237, 0.05125])
        },
        'put': {
            'strikes': np.array([6.3345871849063204, 6.466237127791337, 6.556456642360699, 6.62844676520488, 6.690058194848516, 6.7432490571893675, 6.793099444515628, 6.84094867055488, 6.887804351483665, 6.934523170882112]),
            'vols': np.array([0.05388333333333333, 0.05325, 0.052616666666666666, 0.05198333333333333, 0.05135, 0.05133, 0.05131, 0.051289999999999995, 0.051269999999999996, 0.05125])
        }
    },
    'ON': {
        'call': {
            'strikes': np.array([7.146217904553322, 7.140096524497948, 7.13598024176901, 7.132736775042085, 7.129987327149665, 7.127551658794126, 7.1253320025205715, 7.123263708383072, 7.121300918432771, 7.119407838664755]),
            'vols': np.array([0.043649999999999994, 0.04325, 0.04285, 0.042449999999999995, 0.04205, 0.041639999999999996, 0.041229999999999996, 0.04082, 0.04041, 0.04])
        }
    },
    '1M': {
        'put': {
            'strikes':  np.array([6.859167725933419, 6.913655583461786, 6.950598113722172, 6.9799401770863, 7.005017556334405, 7.027341177726721, 7.047904700347554, 7.067283724783175, 7.085892873466964, 7.1040631832183685]),
            'vols': np.array([0.07430833333333334, 0.07385, 0.07339166666666666, 0.07293333333333334, 0.072475, 0.07207999999999999, 0.071685, 0.07128999999999999, 0.070895, 0.0705])
        }
    },
    '2M': {
        'call': {
            'strikes':  np.array([7.409855463414479, 7.333047278023969, 7.281821505981042, 7.241788004269528, 7.2081423287516175, 7.178967891011616, 7.152476490450044, 7.1278736853925695, 7.104597995789354, 7.08221304078188]),
            'vols': np.array([0.06585, 0.065, 0.06415, 0.0633, 0.06245, 0.06181, 0.061169999999999995, 0.06053, 0.05989, 0.05925])
        }
    },
    '4M': {
        'call': {
            'strikes': np.array([7.5015934616669435, 7.3919141195819416, 7.319116760594353, 7.262665519422753, 7.215691951054631, 7.176078215865435, 7.1403180199612875, 7.107314405158959, 7.07629560616797, 7.046665885742931]),
            'vols': np.array([0.065739, 0.064432, 0.063125, 0.061818000000000005, 0.060511, 0.0596994, 0.058887800000000004, 0.0580762, 0.057264600000000006, 0.056453])
        }
    },
    '5M': {
        'call': {
            'strikes': np.array([7.5335112495776215, 7.410331488832908, 7.328698695690782, 7.265515405729366, 7.213055773063259, 7.168992715538461, 7.129295311614495, 7.092735062959017, 7.058448627444141, 7.025770633037627]),
            'vols': np.array([0.06480033333333332, 0.063424, 0.06204766666666666, 0.060671333333333334, 0.059295, 0.0584348, 0.057574600000000004, 0.0567144, 0.0558542, 0.054994])
        }
    },
    '60D': {
        'put': {
            'strikes': np.array(
                [6.78862023382726, 6.855266214334424, 6.900508163830619, 6.936439190409674, 6.967121821793172, 6.994391268713936, 7.01947082437311, 7.043062481117358, 7.065671811939301, 7.087702293093335]),
            'vols': np.array([0.064488, 0.063991, 0.06349400000000001, 0.062997, 0.0625, 0.0620636, 0.0616272, 0.0611908, 0.0607544, 0.060318])
        }
    },
    '5D': {
        'call': {
            'strikes': np.array(
                [7.17699858861286, 7.163371787365449, 7.1542111416101575, 7.1469852406030805, 7.140848279115399, 7.135339141615131, 7.130329575091909, 7.125672628839256, 7.121264315728749, 7.117023764922904]),
            'vols': np.array([0.04356666666666666, 0.04325, 0.04293333333333333, 0.042616666666666664, 0.0423, 0.041839999999999995, 0.04138, 0.04092, 0.04046, 0.04])
        }
    },
    '6D': {
        'put': {
            'strikes': np.array(
                [6.993461637198943, 7.02098151296903, 7.039583394799938, 7.054338651809356, 7.0669442937084925, 7.078227943067086, 7.0886001329821555, 7.09835461009976, 7.107702011849124, 7.11680944136393]),
            'vols': np.array([0.0829, 0.0825, 0.0821, 0.0817, 0.0813, 0.08084, 0.08038, 0.07992, 0.07946, 0.079])
        }
    },
    '323D': {
        'call': {
            'strikes': np.array(
                [7.6748472795109945, 7.481303865246426, 7.354248097593281, 7.257314570635226, 7.178299007619662, 7.115802624305853, 7.059887385143864, 7.008761614042868, 6.961168879829837, 6.916143175355992]),
            'vols': np.array([0.06586866666666667, 0.063615, 0.06136133333333334, 0.05910766666666667, 0.056854, 0.0558072, 0.0547604, 0.0537136, 0.0526668, 0.05162])
        }
    },
    '218D': {
        'put': {
            'strikes': np.array(
                [6.515611308285169, 6.62433695944781, 6.698550193030625, 6.757611046588919, 6.808053762669025, 6.85193007393258, 6.892695326650154, 6.931461252686839, 6.969046386337704, 7.00612550772994]),
            'vols': np.array([0.05645566666666667, 0.055835, 0.05521433333333334, 0.054593666666666665, 0.053973, 0.0537854, 0.0535978, 0.0534102, 0.0532226, 0.053035])
        }
    }
}
'''
test_cases2 = np.array([
    [7.0495, "4M", "call"],
    [7.0291, "5M", "call"],
])
'''
test_cases = np.array([
    [7.75, "1Y", "call"],
    [7.3, "1Y", "call"],
    [7.1, "1Y", "call"],
    [6.86, "1Y", "put"],
    [6.8, "1Y", "put"],
    [7.0495, "4M", "call"],
    [7.0291, "5M", "call"],
    [6.95, "60D", "put"],  # 2024/12/30   6.9500p
    [7.14, "5D", "call"],  # 2024/11/5  7.1400c
    [7.11, "323D", "call"],  # 2025/9/19  7.1100c
    [7.4, "2M", "call"],
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

#for i in range(len(test_cases2)):
#    interpDeltaStrikes2(test_cases2[i][0], test_cases2[i][1], test_cases2[i][2])

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
