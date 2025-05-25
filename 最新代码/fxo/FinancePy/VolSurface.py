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
mkt_strangle_25d_vols = [0.65, 0.75, 0.85, 0.90, 0.95, 0.85]
rsk_reversal_25d_vols = [-0.20, -0.25, -0.30, -0.50, -0.60, -0.562]
mkt_strangle_10d_vols = [2.433, 2.83, 3.228, 3.485, 3.806, 3.208]
rsk_reversal_10d_vols = [-1.258, -
1.297, -1.332, -1.408, -1.359, -1.208]

mkt_strangle_25d_vols = None
rsk_reversal_25d_vols = None

notional_currency = for_name

atm_method = FinFXATMMethod.FWD_DELTA_NEUTRAL
delta_method = FinFXDeltaMethod.SPOT_DELTA
vol_functionType = VolFuncTypes.CLARK
alpha = 0.50  # FIT WINGS AT 10D if ALPHA = 1.0

fx_market_plus = FXVolSurfacePlus(value_dt,
                                  spot_fx_rate,
                                  currency_pair,
                                  notional_currency,
                                  domestic_curve,
                                  foreign_curve,
                                  tenors,
                                  atm_vols,
                                  mkt_strangle_25d_vols,
                                  rsk_reversal_25d_vols,
                                  mkt_strangle_10d_vols,
                                  rsk_reversal_10d_vols,
                                  alpha,
                                  atm_method,
                                  delta_method,
                                  vol_functionType)

fx_market_plus.check_calibration(False)

years = [1.0 / 12.0, 2. / 12., 0.25, 0.5, 1.0, 2.0]

dates = value_dt.add_years(years)

deltas = np.linspace(0.10, 0.90, 17)

if 1 == 1:
    volSurface = []
    for delta in deltas:
        volSmile = []
        for dt in dates:
            (vol, k) = fx_market_plus.vol_from_delta_date(delta, dt)
            volSmile.append(vol * 100.0)
            print(delta, k, dt, vol * 100.0)

        volSurface.append(volSmile)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    X, Y = np.meshgrid(years, deltas)
    zs = np.array(volSurface)
    Z = zs.reshape(X.shape)

    ax.plot_surface(X, Y, Z)

    ax.set_xlabel('Years')
    ax.set_ylabel('Delta')
    ax.set_zlabel('Volatility')
    plt.title("EURUSD Volatility Surface")
    plt.show()