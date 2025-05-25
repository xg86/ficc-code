import numpy as np
import matplotlib.pyplot as plt

'''
In this notebook I show how you can calibrate to the FX Vol Surface to ATM, 25D MS and 25D RR at one expiry date 
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

#the ATM vol and the market strangle and risk-reversal quotes.
tenors = ['1Y']
atm_vols = [18.250]
ms25DeltaVols = [0.95]
rr25DeltaVols = [-0.60]


notional_currency = for_name
atm_method = FinFXATMMethod.FWD_DELTA_NEUTRAL
delta_method = FinFXDeltaMethod.SPOT_DELTA

fxVolSurfaceClark = FXVolSurface(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                   domestic_curve, foreign_curve,
                                   tenors, atm_vols, ms25DeltaVols, rr25DeltaVols,
                                   atm_method, delta_method, VolFuncTypes.CLARK5)

fxVolSurfaceSABR = FXVolSurface(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                   domestic_curve, foreign_curve,
                                   tenors, atm_vols, ms25DeltaVols, rr25DeltaVols,
                                   atm_method, delta_method, VolFuncTypes.SABR)

fxVolSurfaceBBG = FXVolSurface(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                  domestic_curve, foreign_curve,
                                  tenors,
                               atm_vols,
                               ms25DeltaVols,
                               rr25DeltaVols,
                                  atm_method, delta_method, VolFuncTypes.BBG)

fxVolSurfaceSVI = FXVolSurface(value_dt, spot_fx_rate, currency_pair, notional_currency,
                                  domestic_curve, foreign_curve,
                                  tenors,
                               atm_vols,
                               ms25DeltaVols,
                               rr25DeltaVols,
                                  atm_method, delta_method, VolFuncTypes.SVI)
print(f"*************** fxVolSurfaceSVI ************************")
fxVolSurfaceSVI.check_calibration(False)

#print(f"*************** fxVolSurfaceClark ************************")
#fxVolSurfaceClark.check_calibration(True)

#print(f"*************** fxVolSurfaceSABR ************************")
#fxVolSurfaceSABR.check_calibration(True)

#print(f"**************** fxVolSurfaceBBG ***********************")
#fxVolSurfaceBBG.check_calibration(True)


'''
strikes = np.linspace(0.5, 2.5, 1000)
expiry_dt = value_dt.add_tenor("1Y")

#Volatility Smile Analysis - Different Volatility Function Types
volsClark = []
volsSABR = []
volsBBG = []

for k in strikes:
    volClark = fxVolSurfaceClark.volatility(k, expiry_dt)
    volSABR = fxVolSurfaceSABR.volatility(k, expiry_dt)
    volBBG = fxVolSurfaceBBG.volatility(k, expiry_dt)
    volsClark.append(volClark*100.0)
    volsSABR.append(volSABR*100.0)
    volsBBG.append(volBBG*100.0)

plt.figure(figsize=(10, 6))
plt.plot(strikes, volsClark, label="Clark")
plt.plot(strikes, volsSABR, label="SABR")
plt.plot(strikes, volsBBG, label="BBG")
plt.xlabel("Strike")
plt.ylabel("Black Scholes Volatility (%)")
plt.title("Comparison of Volatility Smiles")
plt.legend()
#plt.show()

#Implied FX Rate Probability Density Functions
lower = 0.50
upper = 2.25
dbnClark = fxVolSurfaceClark.implied_dbns(lower, upper, 1000)
dbnSABR = fxVolSurfaceSABR.implied_dbns(lower, upper, 1000)
dbnBBG = fxVolSurfaceBBG.implied_dbns(lower, upper, 1000)

plt.figure(figsize=(10,6))
plt.plot(dbnClark[0]._x, dbnClark[0]._densitydx, label="Clark")
plt.plot(dbnSABR[0]._x, dbnSABR[0]._densitydx, label="SABR")
plt.plot(dbnBBG[0]._x, dbnBBG[0]._densitydx, label="BBG")
plt.title("Implied Probability Density Function")
plt.legend();
#plt.show()

#Expiry Date Interpolation
k = 1.30
years = np.linspace(0.0, 2.0, 100)
expiry_dts = value_dt.add_years(years)

volsClark = []
volsSABR = []
volsBBG = []

for expiry_dt in expiry_dts:
    volClark = fxVolSurfaceClark.volatility(k, expiry_dt)
    volSABR = fxVolSurfaceSABR.volatility(k, expiry_dt)
    volBBG = fxVolSurfaceBBG.volatility(k, expiry_dt)
    volsClark.append(volClark * 100.0)
    volsSABR.append(volSABR * 100.0)
    volsBBG.append(volBBG * 100.0)

plt.figure(figsize=(10,6))
plt.plot(years, volsClark, label="Clark")
plt.plot(years, volsSABR, label="SABR")
plt.plot(years, volsBBG, label="BBG")
plt.xlabel("Years")
plt.ylabel("Black Scholes Volatility (%)")
plt.title("Comparison of Volatility Time Interpolation")
plt.legend();
plt.show()
'''