import numpy as np
import matplotlib.pyplot as plt
from financepy.market.curves.composite_discount_curve import CompositeDiscountCurve
from financepy.utils import *
from financepy.models.black_scholes import *
from financepy.products.fx import *
from financepy.market.curves import *
from financepy.market.volatility import *
from financepy.market.volatility.fx_vol_surface import FinFXATMMethod
from financepy.market.volatility.fx_vol_surface import FXVolSurface




#Jun 5, 2023

value_dt = Date(5, 6, 2023)

#ccy1
for_name = "USD"
dom_name = "CNY"

# Define the value dates and corresponding rates
zero_rate_dates = [
    Date(14, 6, 2023),
    Date(21, 6, 2023),
    Date(28, 6, 2023),

    Date(7, 7, 2023),
    Date(7, 8, 2023),
    Date(7, 9, 2023),
    Date(7, 10, 2023),
    Date(7, 11, 2023),
    Date(7, 12, 2023),

    Date(7, 1, 2024),
    Date(7, 6, 2024),
    Date(7, 12, 2024),

    Date(7, 6, 2025),
    Date(7, 6, 2026),
    Date(7, 6, 2027),
    Date(7, 6, 2028),

    Date(7, 6, 2029),
    Date(7, 6, 2030),
    Date(7, 6, 2033)
]

usd_rates = np.array([
0.06594,
0.06557,
0.06444,
0.06314,
0.06271,

0.06212,
0.06150,
0.06120,
0.06093,
0.05985,

0.05852,
0.05510,
0.05135,
0.04799,
0.04510,

0.04519,
0.04572,
0.04644,
0.05022])

# Corresponding rates
cny_rates = np.array([0.02218,
0.02218,
0.02219,
0.02219,
0.02221,
0.02223,
0.02221,
0.02221,
0.02222,
0.02289,
0.02322,
0.02443,
0.02513,
0.02707,
0.02895,
0.03100,
0.03267,
0.03408,
0.03816])
'''
usd_curves = []

for rate, val_dt in zip(usd_rates, value_dates):
    curve_flat = DiscountCurveFlat(val_dt, rate)
    usd_curves.append(curve_flat)

cny_curves = []
for rate, val_dt in zip(cny_rates, value_dates):
    curve_flat = DiscountCurveFlat(val_dt, rate)
    cny_curves.append(curve_flat)
'''
domestic_curve = DiscountCurveZeros(
                 value_dt,
                 zero_rate_dates,
                 cny_rates
)

foreign_curve = DiscountCurveZeros(
    value_dt,
    zero_rate_dates,
    usd_rates
)


currency_pair = for_name + dom_name
spot_fx_rate = 7.1226


tenors = ['1W',
'2W',
'3W',
'1M',
'2M',
'3M',
'6M',
'9M',
'1Y',
'18M',
'2Y',
'3Y']

atm_vols = [5.195,
5.293,
5.125,
4.815,
4.690,
4.658,
4.673,
4.722,
4.770,
4.775,
4.755,
4.630]


#RR
rr25DeltaVols = [0.373,
0.365,
0.383,
0.475,
0.450,
0.453,
0.355,
0.342,
0.353,
0.357,
0.363,
0.388]

rr10DeltaVols = [0.495,
0.535,
0.604,
0.505,
0.570,
0.595,
0.673,
0.727,
0.788,
0.870,
0.870,
0.847]

##ms is same as  BF, see FXVolSurfacePlus line 1822
ms25DeltaVols = [0.238,
0.278,
0.218,
0.226,
0.225,
0.230,
0.263,
0.263,
0.278,
0.273,
0.277,
0.300]
ms10DeltaVols = [0.480,
0.545,
0.515,
0.466,
0.475,
0.424,
0.575,
0.601,
0.620,
0.575,
0.585,
0.593]


notional_currency = for_name
atm_method = FinFXATMMethod.FWD_DELTA_NEUTRAL
#delta_method = FinFXDeltaMethod.SPOT_DELTA
#delta_method = FinFXDeltaMethod.FORWARD_DELTA
delta_method = FinFXDeltaMethod.SPOT_DELTA
#alpha is weight, using 25 only 0, using 10 is 1. both is 0.5
alpha = 0.5
alpha_25 = 0
alpha_10 = 1

fxVolSurfaceBBG_25 = FXVolSurfacePlus(value_dt,
                                   spot_fx_rate,
                                   currency_pair,
                                   notional_currency,
                                   domestic_curve,
                                   foreign_curve,
                                   tenors, atm_vols,
                                   ms25DeltaVols, rr25DeltaVols,
                                   [], [],
                                   alpha_25,
                                   atm_method, delta_method,
                                   VolFuncTypes.BBG)

fxVolSurfaceBBG_10 = FXVolSurfacePlus(value_dt,
                                   spot_fx_rate,
                                   currency_pair,
                                   notional_currency,
                                   domestic_curve,
                                   foreign_curve,
                                   tenors, atm_vols,
                                   [], [],
                                   ms10DeltaVols, rr10DeltaVols,
                                   alpha_10,
                                   atm_method, delta_method,
                                   VolFuncTypes.BBG)
fxVolSurfaceBBG_CLARK_25_10 = FXVolSurfacePlus(value_dt,
                                   spot_fx_rate,
                                   currency_pair,
                                   notional_currency,
                                   domestic_curve,
                                   foreign_curve,
                                   tenors, atm_vols,
                                   ms25DeltaVols, rr25DeltaVols,
                                   ms10DeltaVols, rr10DeltaVols,
                                   alpha,
                                   atm_method, delta_method,
                                   VolFuncTypes.CLARK)

#fxVolSurfaceBBG_25_10.check_calibration(True)

#print(fxVolSurfaceBBG.k_25d_c)
#print(fxVolSurfaceBBG.k_25d_p)

expiry_dts = value_dt.add_tenor(tenors)


def get_vol_from_delta_maturity_date(volSurface:FXVolSurface, delta: int, expiry_dt:Date):
    vol_call, k_call = volSurface.vol_from_delta_date(delta/100, expiry_dt, 1)
    print("expiry_dts", expiry_dt, "delta", delta, "vol_call", vol_call, "k_call", k_call)
    vol_put, k_put = volSurface.vol_from_delta_date(delta/100, expiry_dt, 0)
    print("expiry_dts", expiry_dt, "delta", delta,  "vol_put", vol_put, "k_put", k_put)




for i in range(0, len(expiry_dts)):
    expiry_dt = expiry_dts[i]
    print("******************* fxVolSurfaceBBG_25 ******************")
    get_vol_from_delta_maturity_date(fxVolSurfaceBBG_25, 35, expiry_dt)
    get_vol_from_delta_maturity_date(fxVolSurfaceBBG_25, 15, expiry_dt)
    get_vol_from_delta_maturity_date(fxVolSurfaceBBG_25, 5, expiry_dt)
'''
for i in range(0, len(expiry_dts)):
    #fwd = fxVolSurfaceBBG.fwd[i]
    #k_25_c = fxVolSurfaceBBG.k_25d_c[i]
    #vol_25_c = fxVolSurfaceBBG.vol_from_strike_date(k_25_c, expiry_dts[i])
    #print("expiry_dts", expiry_dts[i], "fwd", fwd, "k25_c", k_25_c, "vol_25_c", vol_25_c*100)
    #vol_15_c, k_15_c = fxVolSurfaceBBG.vol_from_delta_date(0.15, expiry_dts[i])
    #print("expiry_dts", expiry_dts[i], "vol_15_c", vol_15_c, 'k_15_c', k_15_c)
    #vol_15_p, k_15_p = fxVolSurfaceBBG.vol_from_delta_date(0.15, expiry_dts[i], 0)
    #print("expiry_dts", expiry_dts[i], "vol_15_p", vol_15_p, 'k_15_p', k_15_p)
    #vol_35_c, k_35_c = fxVolSurfaceBBG.vol_from_delta_date(0.35, expiry_dts[i])
    #print("expiry_dts", expiry_dts[i], "vol_35_c", vol_35_c, 'k_35_c', k_35_c)
    #vol_35_p, k_35_p = fxVolSurfaceBBG.vol_from_delta_date(0.35, expiry_dts[i], 0)
    #print("expiry_dts", expiry_dts[i], "vol_35_p", vol_35_p, 'k_35_p', k_35_p)

    vol_5_c, k_5_c = fxVolSurfaceBBG.vol_from_delta_date(0.05, expiry_dts[i])
    print("expiry_dts", expiry_dts[i], "vol_5_c", vol_5_c, 'k_5_c', k_5_c)
    vol_5_p, k_5_p = fxVolSurfaceBBG.vol_from_delta_date(0.05, expiry_dts[i], 0)
    print("expiry_dts", expiry_dts[i], "vol_5_p", vol_5_p, 'k_5_p', k_5_p)
'''