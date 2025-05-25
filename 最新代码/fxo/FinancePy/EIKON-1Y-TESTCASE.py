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

value_dt = Date(27, 6, 2023)

for_name = "USD"
dom_name = "CNY"
for_cc_rate = 0.06007 # USD
dom_cc_rate = 0.02374 # CNY

domestic_curve = DiscountCurveFlat(value_dt, dom_cc_rate)
foreign_curve = DiscountCurveFlat(value_dt, for_cc_rate)


domestic_curve = DiscountCurveFlat(value_dt, dom_cc_rate)
foreign_curve = DiscountCurveFlat(value_dt, for_cc_rate)

currency_pair = for_name + dom_name
spot_fx_rate = 7.2202

tenors = ['1Y']
atm_vols = [4.537]
ms25DeltaVols = [0.1315]
rr25DeltaVols = [0.357]
ms10DeltaVols = [0.5485]
rr10DeltaVols = [0.689]

notional_currency = for_name
atm_method = FinFXATMMethod.FWD_DELTA_NEUTRAL
delta_method = FinFXDeltaMethod.FORWARD_DELTA
#delta_method = FinFXDeltaMethod.SPOT_DELTA
#25D only
alpha = 0.5
alpha_15 = 0
alpha_10 = 1

'''
print("******************* fxVolSurfaceBBG_25 ******************")
fxVolSurfaceBBG_25 = FXVolSurface(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                  domestic_curve, foreign_curve,
                                  tenors,
                               atm_vols,
                               ms25DeltaVols,
                               rr25DeltaVols,
                                  atm_method, delta_method, VolFuncTypes.BBG)
fxVolSurfaceBBG_25.check_calibration(True)
'''
print("******************* fxVolSurfaceBBG_25_10 ******************")
fxVolSurface = FXVolSurfacePlus(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                       domestic_curve, foreign_curve,
                                       tenors, atm_vols,
                                       ms25DeltaVols,
                                       rr25DeltaVols,
                                       ms10DeltaVols,
                                       rr10DeltaVols,
                                       alpha,
                                       atm_method, delta_method,
                                       VolFuncTypes.SABR)

fxVolSurface.check_calibration(False)


#print(fxVolSurfaceBBG_25.k_25d_c)
#print(fxVolSurfaceBBG_25.k_25d_p)

#print(fxVolSurfaceBBG.k_25d_p)
#print(fxVolSurfaceBBG.k_10d_p)

def get_vol_from_delta_maturity_date(volSurface:FXVolSurface, delta: int, expiry_dt:Date):
    vol_call, k_call = volSurface.vol_from_delta_date(delta/100, expiry_dt, 1)
    print("expiry_dts", expiry_dt, "delta", delta, "vol_call", vol_call, "k_call", k_call)
    vol_put, k_put = volSurface.vol_from_delta_date(delta/100, expiry_dt, 0)
    print("expiry_dts", expiry_dt, "delta", delta,  "vol_put", vol_put, "k_put", k_put)

expiry_dt = Date(27, 6, 2024)

get_vol_from_delta_maturity_date(fxVolSurface, 25, expiry_dt)
get_vol_from_delta_maturity_date(fxVolSurface, 10, expiry_dt)
#get_vol_from_delta_maturity_date(fxVolSurfaceBBG_25_10, 35, expiry_dt)
#get_vol_from_delta_maturity_date(fxVolSurfaceBBG_25_10, 15, expiry_dt)
#get_vol_from_delta_maturity_date(fxVolSurfaceBBG_25_10, 5, expiry_dt)