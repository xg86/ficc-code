import numpy as np
from scipy.interpolate import interp1d
from FXOptionDeltaStrikeCalculator import FXOptionDeltaStrikeCalculator

# Sample data: delta and implied volatility pairs
deltas = np.array([50, 25, 10])
target_deltas = np.array([5, 10, 15, 20, 25, 30, 35, 40, 45, 50])

delta_vols_maxtrix = {
    '1Y': {
        'call': {
            'strikes': None,
            'vols': np.array([0.051250, 0.056850, 0.064250])
        },
        'put': {
            'strikes': None,
            'vols': np.array([0.051250, 0.051350, 0.053250])
        }
    },
    'ON': {
        'call': {
            'strikes': None,
            'vols': np.array([0.040000, 0.042050, 0.043250])
        }
    },
    '1M': {
        'put': {
            'strikes':  None,
            'vols': np.array([0.070500,0.072475,0.073850])
        }
    },
    '2M': {
        'call': {
            'strikes':  None,
            'vols': np.array([0.059250, 0.062450, 0.065000])
        }
    },
    '120D': {
        'call': {
            'strikes': None,
            'vols': np.array([0.056453, 0.060511, 0.064432])
        }
    },
    '153D': {
        'call': {
            'vols': np.array([0.054994,0.059295, 0.063424])
        }
    },
    '60D': {
        'put': {
            'strikes': None,
            'vols': np.array([0.060318,	0.062500,	0.063991])
        }
    },
    '5D': {
        'call': {
            'strikes': None,
             'vols': np.array([0.040000, 0.042300, 0.043250])
        }
    },
    '6D': {
        'put': {
            'strikes': None,
            'vols': np.array([0.079000,	0.081300, 0.082500])
        }
    },
    '180D': { #6M
        'put': {
            'strikes': None,
             'vols': np.array([0.0538, 0.0548, 0.0566])
        }
    },
    '218D': { #6M
        'put': {
            'strikes': None,
             'vols': np.array([0.053035, 0.053973, 0.055835])
        }
    },
    '273D': { #9M
        'put': {
            'strikes': None,
            'vols': np.array([0.0520, 0.0528, 0.0548])
        }
    },
    '323D': {
        'call': {
            'strikes': None,
            'vols': np.array([0.051620, 0.056854, 0.063615])
        }
    }
}


def interpDeltaVols( target_delta: int, tenor: str, optionType: str, kindMetheod: str= 'linear', interpMethod: str= 'extrapolate'):
    delta_vols = delta_vols_maxtrix[tenor][optionType]['vols']
    vols = interp1d(deltas, delta_vols, kind='linear', fill_value="extrapolate")
    vol = vols(target_delta)
    print(f"{optionType} Option at {tenor} with delta {target_delta}: vol -> {vol:.6f}")
    vol.tolist()
    return vol.max()

def getDeltaVols (tenor: str, optionType: str):
    delta_vols = delta_vols_maxtrix[tenor][optionType]['vols']
    result_vols = []
    result_strikes = []
    for i in range(len(target_deltas)):
        if(target_deltas[i] == 10): # 10D
            result_vols.append(delta_vols[2])
            result_strikes.append(getStrike(delta_vols[2], tenor, target_deltas[i], optionType))
        elif( target_deltas[i] == 25): # 25D
            result_vols.append(delta_vols[1])
            result_strikes.append(getStrike(delta_vols[1], tenor, target_deltas[i], optionType))
        elif(target_deltas[i] == 50):
            result_vols.append(delta_vols[0])
            result_strikes.append(getStrike(delta_vols[0], tenor, target_deltas[i], optionType))
        else:
            vol = interpDeltaVols(target_deltas[i], tenor, optionType)
            result_vols.append(vol)
            result_strikes.append(getStrike(vol, tenor, target_deltas[i], optionType))
    print(f"{optionType} Option at {tenor} combined_vols {result_vols}")
    print(f"{optionType} Option at {tenor} combined_strikes {result_strikes}")

def getStrike(iv: float, T: str, target_delta: float, optionType: str):
    if T == '1Y':
        time_to_maturity = 1
    elif T == 'ON':
        time_to_maturity = 1/365
    elif T == '1M':
        time_to_maturity = 30/365
    elif T == '2M':
        time_to_maturity = 63/365
    elif T == '5D':
        time_to_maturity = 5/365
    elif T == '6D':
        time_to_maturity = 6/365
    elif T == '218D':
        time_to_maturity = 218/365
    elif T == '120D':
        time_to_maturity = 120/365
    elif T == '153D':
        time_to_maturity = 153/365
    elif T == '60D':
        time_to_maturity = 60/365
    elif T == '323D':
        time_to_maturity = 323/365
    else:
        time_to_maturity = 0

    calculator = FXOptionDeltaStrikeCalculator(
        spot=7.12000,
        domestic_rate=0.0192927,
        foreign_rate=0.0503185,
        volatility=iv,
        time_to_maturity=time_to_maturity
    )

    strike_for_target_delta = calculator.find_strike_for_delta(target_delta/100 if optionType == 'call' else target_delta/100*-1, option_type=optionType)
    print(f"The strike price for a {target_delta:.0f}-delta {optionType} is: {strike_for_target_delta:.4f}")
    return strike_for_target_delta

#getDeltaVols('1Y', 'call')
#getDeltaVols('1Y', 'put')
#getDeltaVols('1M', 'put')
#getDeltaVols('2M', 'call')
#getDeltaVols('ON', 'call')
#getDeltaVols('5D', 'call')
#getDeltaVols('6D', 'put')
#getDeltaVols('218D', 'put')
#getDeltaVols('120D', 'call')
#getDeltaVols('153D', 'call')
#getDeltaVols('60D', 'put')
getDeltaVols('323D', 'call')