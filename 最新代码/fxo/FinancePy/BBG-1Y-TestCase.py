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
for_cc_rate = 0.05032 # USD
dom_cc_rate = 0.01929 # CNY

domestic_curve = DiscountCurveFlat(value_dt, dom_cc_rate)
foreign_curve = DiscountCurveFlat(value_dt, for_cc_rate)


domestic_curve = DiscountCurveFlat(value_dt, dom_cc_rate)
foreign_curve = DiscountCurveFlat(value_dt, for_cc_rate)

currency_pair = for_name + dom_name
spot_fx_rate = 7.12

tenors = ['1Y']
'''
atm_vols = [4.77]
ms25DeltaVols = [0.2775]
rr25DeltaVols = [0.355]
ms10DeltaVols = [0.62]
rr10DeltaVols = [0.788]
'''
atm_vols = [5.125]
ms25DeltaVols = [0.285]
rr25DeltaVols = [0.55]
ms10DeltaVols = [0.75]
rr10DeltaVols = [1.1]

notional_currency = for_name
atm_method = FinFXATMMethod.FWD_DELTA_NEUTRAL
delta_method = FinFXDeltaMethod.FORWARD_DELTA
alpha = 0.50




'''
print("******************* fxVolSurfaceSVI ******************")
fxVolSurfaceSVI = FXVolSurface(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                       domestic_curve, foreign_curve,
                                       tenors, atm_vols,
                                       ms25DeltaVols,
                                       rr25DeltaVols,
                                       atm_method, delta_method,
                                       VolFuncTypes.SVI)

fxVolSurfaceSVI.check_calibration(False)
print("******************* fxVolSurfaceSSVI ******************")
fxVolSurfaceSSVI = FXVolSurfacePlus(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                       domestic_curve, foreign_curve,
                                       tenors, atm_vols,
                                       ms25DeltaVols,
                                       rr25DeltaVols,
                                       ms10DeltaVols,
                                       rr10DeltaVols,
                                       alpha,
                                       atm_method, delta_method,
                                       VolFuncTypes.SSVI)
fxVolSurfaceSSVI.check_calibration(False)
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

fxVolSurfaceBBG_25_10.check_calibration(False)

'''
print("******************* fxVolSurfaceSABR ******************")
fxVolSurfaceSABR = FXVolSurfacePlus(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                       domestic_curve, foreign_curve,
                                       tenors, atm_vols,
                                       ms25DeltaVols,
                                       rr25DeltaVols,
                                       ms10DeltaVols,
                                       rr10DeltaVols,
                                       alpha,
                                       atm_method, delta_method,
                                       VolFuncTypes.SABR)
fxVolSurfaceSABR.check_calibration(False)

print("******************* fxVolSurfaceCLARK ******************")
fxVolSurfaceCLARK = FXVolSurfacePlus(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                       domestic_curve, foreign_curve,
                                       tenors, atm_vols,
                                       ms25DeltaVols,
                                       rr25DeltaVols,
                                       ms10DeltaVols,
                                       rr10DeltaVols,
                                       alpha,
                                       atm_method, delta_method,
                                       VolFuncTypes.CLARK)
fxVolSurfaceCLARK.check_calibration(False)

print("******************* fxVolSurfaceCLARK5 ******************")
fxVolSurfaceCLARK5 = FXVolSurfacePlus(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                       domestic_curve, foreign_curve,
                                       tenors, atm_vols,
                                       ms25DeltaVols,
                                       rr25DeltaVols,
                                       ms10DeltaVols,
                                       rr10DeltaVols,
                                       alpha,
                                       atm_method, delta_method,
                                       VolFuncTypes.CLARK5)
fxVolSurfaceCLARK5.check_calibration(False)
'''

'''
print("******************* fxVolSurfaceSABR_BETA_ONE ******************")
fxVolSurfaceSABR_BETA_ONE = FXVolSurfacePlus(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                       domestic_curve, foreign_curve,
                                       tenors, atm_vols,
                                       ms25DeltaVols,
                                       rr25DeltaVols,
                                       ms10DeltaVols,
                                       rr10DeltaVols,
                                       alpha,
                                       atm_method, delta_method,
                                       VolFuncTypes.SABR_BETA_ONE)
fxVolSurfaceSABR_BETA_ONE.check_calibration(False)

print("******************* fxVolSurfaceSABR_BETA_HALF ******************")
fxVolSurfaceSABR_BETA_HALF = FXVolSurfacePlus(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                       domestic_curve, foreign_curve,
                                       tenors, atm_vols,
                                       ms25DeltaVols,
                                       rr25DeltaVols,
                                       ms10DeltaVols,
                                       rr10DeltaVols,
                                       alpha,
                                       atm_method, delta_method,
                                       VolFuncTypes.SABR_BETA_HALF)
fxVolSurfaceSABR_BETA_HALF.check_calibration(False)


#print(fxVolSurfaceBBG.k_25d_c)
#print(fxVolSurfaceBBG.k_25d_p)

#print(fxVolSurfaceBBG.k_25d_p)
#print(fxVolSurfaceBBG.k_10d_p)

expiry_dt = Date(31, 10, 2025)
vol_25_c = fxVolSurfaceBBG.vol_from_delta_date(0.25, expiry_dt, 1)
print("expiry_dts", expiry_dt, "vol_25_c", vol_25_c)
vol_25_p = fxVolSurfaceBBG.vol_from_delta_date(0.25, expiry_dt, 0)
print("expiry_dts", expiry_dt, "vol_25_p", vol_25_p)
'''