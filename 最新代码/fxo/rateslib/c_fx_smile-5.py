from rateslib.curves import Curve
from rateslib.solver import Solver
from rateslib.fx import FXForwards, FXRates
from rateslib.instruments import FXStraddle, FXRiskReversal, FXBrokerFly, Value
from rateslib.fx_volatility import FXDeltaVolSmile, FXDeltaVolSurface
from datetime import datetime as dt
from matplotlib import pyplot as plt
import numpy as np
eur = Curve({dt(2009, 5, 3): 1.0, dt(2011, 5, 10): 1.0})
usd = Curve({dt(2009, 5, 3): 1.0, dt(2011, 5, 10): 1.0})
fxf = FXForwards(
    fx_rates=FXRates({"eurusd": 1.34664}, settlement=dt(2009, 5, 5)),
    fx_curves={"eureur": eur, "usdusd": usd, "eurusd": eur},
)
solver = Solver(
    curves=[eur, usd],
    instruments=[
        Value(dt(2009, 5, 4), curves=eur, metric="cc_zero_rate"),
        Value(dt(2009, 5, 4), curves=usd, metric="cc_zero_rate")
    ],
    s=[1.00, 0.4759550366220911],
    fx=fxf,
)
surface = FXDeltaVolSurface(
    eval_date=dt(2009, 5, 3),
    delta_indexes=[0.25, 0.5, 0.75],
    expiries=[dt(2010, 5, 3), dt(2011, 5, 3)],
    node_values=np.ones((2, 3))* 18.0,
    delta_type="forward",
    id="surface",
)
fx_args_0 = dict(
    pair="eurusd",
    curves=[None, eur, None, usd],
    expiry=dt(2010, 5, 3),
    delta_type="spot",
    vol="surface",
)
fx_args_1 = dict(
    pair="eurusd",
    curves=[None, eur, None, usd],
    expiry=dt(2011, 5, 3),
    delta_type="forward",
    vol="surface",
)

solver = Solver(
    surfaces=[surface],
    instruments=[
        FXStraddle(strike="atm_delta", **fx_args_0),
        FXBrokerFly(strike=["-25d", "atm_delta", "25d"], **fx_args_0),
        FXRiskReversal(strike=["-25d", "25d"], **fx_args_0),
        FXStraddle(strike="atm_delta", **fx_args_1),
        FXBrokerFly(strike=["-25d", "atm_delta", "25d"], **fx_args_1),
        FXRiskReversal(strike=["-25d", "25d"], **fx_args_1),
    ],
    s=[18.25, 0.95, -0.6, 17.677, 0.85, -0.562],
    fx=fxf,
)
fig, ax, lines = surface.plot()
plt.show()
plt.close()