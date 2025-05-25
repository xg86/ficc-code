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

value_dt = Date(5, 6, 2023)

for_name = "USD"
dom_name = "CNY"
for_cc_rate = 0.05852 # USD
dom_cc_rate = 0.023220 # CNY

domestic_curve = DiscountCurveFlat(value_dt, dom_cc_rate)
foreign_curve = DiscountCurveFlat(value_dt, for_cc_rate)


domestic_curve = DiscountCurveFlat(value_dt, dom_cc_rate)
foreign_curve = DiscountCurveFlat(value_dt, for_cc_rate)

currency_pair = for_name + dom_name
spot_fx_rate = 7.1226

tenors = ['1Y']

atm_vols = [4.77]
ms25DeltaVols = [0.2775]
rr25DeltaVols = [0.353]
ms10DeltaVols = [0.62]
rr10DeltaVols = [0.788]


notional_currency = for_name
atm_method = FinFXATMMethod.FWD_DELTA_NEUTRAL
#delta_method = FinFXDeltaMethod.FORWARD_DELTA

delta_method = FinFXDeltaMethod.SPOT_DELTA
alpha_25 = 0
alpha_10 = 1
alpha = 0.5
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
print("******************* fxVolSurfaceBBG_25******************")
fxVolSurfaceBBG_25 = FXVolSurfacePlus(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                      domestic_curve, foreign_curve,
                                      tenors, atm_vols,
                                      ms25DeltaVols,
                                      rr25DeltaVols,
                                      [],
                                      [],
                                      alpha_25,
                                      atm_method, delta_method,
                                      VolFuncTypes.BBG)
fxVolSurfaceBBG_25.check_calibration(False)
print("******************* fxVolSurfaceBBG_10 ******************")
fxVolSurfaceBBG_10 = FXVolSurfacePlus(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                      domestic_curve, foreign_curve,
                                      tenors, atm_vols,
                                      [],
                                      [],
                                      ms10DeltaVols,
                                      rr10DeltaVols,
                                      alpha_10,
                                      atm_method, delta_method,
                                      VolFuncTypes.BBG)
fxVolSurfaceBBG_10.check_calibration(False)

print("******************* fxVolSurfaceBBG_25_10 ******************")
fxVolSurfaceBBG_25_10 = FXVolSurfacePlus(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                      domestic_curve, foreign_curve,
                                      tenors, atm_vols,
                                         ms25DeltaVols,
                                         rr25DeltaVols,
                                      ms10DeltaVols,
                                      rr10DeltaVols,
                                      alpha,
                                      atm_method, delta_method,
                                      VolFuncTypes.BBG)

fxVolSurfaceBBG_25_10.check_calibration(True)

def get_vol_from_delta_maturity_date(volSurface:FXVolSurface, delta: int, expiry_dt:Date):
    vol_call, k_call = volSurface.vol_from_delta_date(delta/100, expiry_dt, 1)
    print("expiry_dts", expiry_dt, "delta", delta, "vol_call", vol_call, "k_call", k_call)
    vol_put, k_put = volSurface.vol_from_delta_date(delta/100, expiry_dt, 0)
    print("expiry_dts", expiry_dt, "delta", delta,  "vol_put", vol_put, "k_put", k_put)

expiry_dt = Date(5, 6, 2024)
print("******************* fxVolSurfaceBBG_25 1Y ******************")
get_vol_from_delta_maturity_date(fxVolSurfaceBBG_25, 25, expiry_dt)
get_vol_from_delta_maturity_date(fxVolSurfaceBBG_25, 10, expiry_dt)
get_vol_from_delta_maturity_date(fxVolSurfaceBBG_25, 35, expiry_dt)
get_vol_from_delta_maturity_date(fxVolSurfaceBBG_25, 15, expiry_dt)
get_vol_from_delta_maturity_date(fxVolSurfaceBBG_25, 5, expiry_dt)
print("******************* fxVolSurfaceBBG_10 1Y ******************")
get_vol_from_delta_maturity_date(fxVolSurfaceBBG_10, 25, expiry_dt)
get_vol_from_delta_maturity_date(fxVolSurfaceBBG_10, 10, expiry_dt)
get_vol_from_delta_maturity_date(fxVolSurfaceBBG_10, 35, expiry_dt)
get_vol_from_delta_maturity_date(fxVolSurfaceBBG_10, 15, expiry_dt)
get_vol_from_delta_maturity_date(fxVolSurfaceBBG_10, 5, expiry_dt)