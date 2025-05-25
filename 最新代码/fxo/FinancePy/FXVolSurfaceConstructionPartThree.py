import numpy as np
import matplotlib.pyplot as plt

'''
In this notebook I show how you can calibrate to the FX Vol Surface to ATM, 25D and 10D at multiple expiry dates 
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


tenors = ['1M', '2M', '3M', '6M', '1Y', '2Y']
atm_vols = [21.00, 21.00, 20.750, 19.400, 18.250, 17.677]
ms25DeltaVols = [0.65, 0.75, 0.85, 0.90, 0.95, 0.85]
rr25DeltaVols = [-0.20, -0.25, -0.30, -0.50, -0.60, -0.562]
ms10DeltaVols = [2.433, 2.83, 3.228, 3.485, 3.806, 3.208]
rr10DeltaVols = [-1.258, -1.297, -1.332, -1.408, -1.359, -1.208]


notional_currency = for_name
atm_method = FinFXATMMethod.FWD_DELTA_NEUTRAL
delta_method = FinFXDeltaMethod.SPOT_DELTA
alpha = 0.5


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
                                       ms10DeltaVols, rr10DeltaVols,
                                       alpha,
                                       atm_method, delta_method,
                                       VolFuncTypes.BBG)

print(f"*************** fxVolSurfaceClark ************************")
#fxVolSurfaceClark.check_calibration(True)

print(f"*************** fxVolSurfaceSABR ************************")
#fxVolSurfaceSABR.check_calibration(True)

print(f"**************** fxVolSurfaceBBG ***********************")
#fxVolSurfaceBBG.check_calibration(True)


expiry_dts = value_dt.add_tenor(tenors)

for i in range(0, len(expiry_dts)):
    fwd = fxVolSurfaceClark.fwd[i]
    kATM = fxVolSurfaceClark.k_atm[i]
    vATM = fxVolSurfaceClark.atm_vols[i]
    volClark = fxVolSurfaceClark.vol_from_strike_date(kATM, expiry_dts[i])
    print("fwd", fwd, "KATM", kATM, "volATM", vATM*100, "volInterp", volClark*100)