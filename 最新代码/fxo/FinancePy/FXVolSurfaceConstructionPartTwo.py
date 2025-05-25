import numpy as np
import matplotlib.pyplot as plt

'''
In this notebook I show how you can calibrate to the FX Vol Surface to ATM, 25D and 10D at one expiry date 
and analyse different volatility interpolation methods.
'''

from financepy.utils import *

from financepy.models.black_scholes import *
from financepy.products.fx import *
from financepy.market.curves import DiscountCurveFlat
from financepy.market.volatility import *
from financepy.market.volatility.fx_vol_surface import FinFXATMMethod
from financepy.market.volatility.fx_vol_surface import FXVolSurface

value_dt = Date(10, 4, 2020)

for_name = "EUR"
dom_name = "USD"
for_cc_rate = 0.03460  # EUR
dom_cc_rate = 0.02940  # USD

domestic_curve = DiscountCurveFlat(value_dt, dom_cc_rate)
foreign_curve = DiscountCurveFlat(value_dt, for_cc_rate)


currency_pair = for_name + dom_name
spot_fx_rate = 1.3465

tenors = ['1Y']
atm_vols = [18.250]
ms25DeltaVols = [0.95]
rr25DeltaVols = [-0.60]
ms10DeltaVols = [3.806]
rr10DeltaVols = [-1.359]


notional_currency = for_name
atm_method = FinFXATMMethod.FWD_DELTA_NEUTRAL
delta_method = FinFXDeltaMethod.SPOT_DELTA
alpha = 0.50

fxVolSurfaceClark = FXVolSurfacePlus(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                       domestic_curve, foreign_curve,
                                       tenors, atm_vols,
                                        ms25DeltaVols, rr25DeltaVols,
                                        ms10DeltaVols, rr10DeltaVols,
                                        alpha,
                                        atm_method, delta_method,
                                        VolFuncTypes.CLARK)

fxVolSurfaceSABR = FXVolSurfacePlus(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                       domestic_curve, foreign_curve,
                                       tenors, atm_vols,
                                       ms25DeltaVols, rr25DeltaVols,
                                       ms10DeltaVols, rr10DeltaVols,
                                       alpha,
                                       atm_method, delta_method,
                                       VolFuncTypes.SABR)

fxVolSurfaceBBG = FXVolSurfacePlus(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                       domestic_curve, foreign_curve,
                                       tenors, atm_vols,
                                       ms25DeltaVols, rr25DeltaVols,
                                       ms10DeltaVols, rr25DeltaVols,
                                       alpha,
                                       atm_method, delta_method,
                                       VolFuncTypes.BBG)

print(f"*************** fxVolSurfaceClark ************************")
#fxVolSurfaceClark.check_calibration(True)

print(f"*************** fxVolSurfaceSABR ************************")
#fxVolSurfaceSABR.check_calibration(True)

print(f"**************** fxVolSurfaceBBG ***********************")
print(fxVolSurfaceBBG.k_25d_c)
#fxVolSurfaceBBG.check_calibration(True)