from rateslib.curves import Curve
from rateslib.instruments import *
from rateslib.fx_volatility import FXDeltaVolSmile
from rateslib.fx import FXRates, FXForwards
from rateslib.solver import Solver
import matplotlib.pyplot as plt
from datetime import datetime as dt
smile = FXDeltaVolSmile(
    nodes={
        0.10: 10.0,
        0.25: 10.0,
        0.50: 10.0,
        0.75: 10.0,
        0.90: 10.0,
    },
    eval_date=dt(2024, 5, 7),
    expiry=dt(2024, 5, 28),
    delta_type="spot",
    id="eurusd_3w_smile"
)
# Define the interest rate curves for EUR, USD and X-Ccy basis
eureur = Curve({dt(2024, 5, 7): 1.0, dt(2024, 5, 30): 1.0}, calendar="tgt", id="eureur")
eurusd = Curve({dt(2024, 5, 7): 1.0, dt(2024, 5, 30): 1.0}, id="eurusd")
usdusd = Curve({dt(2024, 5, 7): 1.0, dt(2024, 5, 30): 1.0}, calendar="nyc", id="usdusd")
# Create an FX Forward market with spot FX rate data
fxf = FXForwards(
    fx_rates=FXRates({"eurusd": 1.0760}, settlement=dt(2024, 5, 9)),
    fx_curves={"eureur": eureur, "usdusd": usdusd, "eurusd": eurusd},
)
# Setup the Solver instrument calibration for rates Curves and vol Smiles
option_args=dict(
    pair="eurusd", expiry=dt(2024, 5, 28), calendar="tgt", delta_type="spot",
    curves=[None, "eurusd", None, "usdusd"], vol="eurusd_3w_smile"
)
solver = Solver(
    curves=[eureur, eurusd, usdusd, smile],
    instruments=[
        IRS(dt(2024, 5, 9), "3W", spec="eur_irs", curves="eureur"),
        IRS(dt(2024, 5, 9), "3W", spec="usd_irs", curves="usdusd"),
        FXSwap(dt(2024, 5, 9), "3W", currency="eur", leg2_currency="usd", curves=[None, "eurusd", None, "usdusd"]),
        FXStraddle(strike="atm_delta", **option_args),
        FXRiskReversal(strike=["-25d", "25d"], **option_args),
        FXRiskReversal(strike=["-10d", "10d"], **option_args),
        FXBrokerFly(strike=["-25d", "atm_delta", "25d"], **option_args),
        FXBrokerFly(strike=["-10d", "atm_delta", "10d"], **option_args),
    ],
    s=[3.90, 5.32, 8.85, 5.493, -0.157, -0.289, 0.071, 0.238],
    fx=fxf,
)
fig, ax, line = smile.plot()
plt.show()
plt.close()