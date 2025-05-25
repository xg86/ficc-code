from rateslib.curves import Curve
from rateslib.instruments import *
from rateslib.fx_volatility import FXDeltaVolSmile
from rateslib.fx import FXRates, FXForwards
from rateslib.solver import Solver
import matplotlib.pyplot as plt
from datetime import datetime as dt

eval_date = dt(2023, 6, 5)
spot_settl_date = dt(2023, 6, 7)
expiry_date = dt(2024, 7, 5)

smile = FXDeltaVolSmile(
    nodes={
        0.10: 10.0,
        0.25: 10.0,
        0.50: 10.0,
        0.75: 10.0,
        0.90: 10.0,
    },
    eval_date=eval_date,
    expiry=expiry_date,
    delta_type="spot",
    id="usdcny_1m_smile"
)

# Define the interest rate curves for EUR, USD and X-Ccy basis
cnycny = Curve({eval_date: 1.0, expiry_date: 1.0}, calendar="tgt", id="cnycny") # using tgt as no cny
usdcny = Curve({eval_date: 1.0, expiry_date: 1.0}, id="usdcny")
usdusd = Curve({eval_date: 1.0, expiry_date: 1.0}, calendar="nyc", id="usdusd")

# Create an FX Forward market with spot FX rate data
fxf = FXForwards(
    fx_rates=FXRates({"usdcny": 7.1226}, settlement=spot_settl_date),
    fx_curves={"cnycny": cnycny, "usdusd": usdusd, "usdcny": usdcny},
)
# Setup the Solver instrument calibration for rates Curves and vol Smiles
option_args=dict(
    pair="usdcny", expiry=expiry_date, calendar="tgt", delta_type="spot",
    curves=[None, "usdcny", None, "cnycny"], vol="usdcny_1m_smile"
)
solver = Solver(
    curves=[cnycny, usdcny, usdusd, smile],
    instruments=[
        IRS(spot_settl_date, "1M", spec="usd_irs", curves="usdusd"),
        IRS(spot_settl_date, "1M", spec="eur_irs", curves="cnycny"),
        FXSwap(spot_settl_date, "1M", currency="usd", leg2_currency="cny", curves=[None, "usdcny", None, "cnycny"]),
        FXStraddle(strike="atm_delta", **option_args),
        FXRiskReversal(strike=["-25d", "25d"], **option_args),
        FXRiskReversal(strike=["-10d", "10d"], **option_args),
        FXBrokerFly(strike=["-25d", "atm_delta", "25d"], **option_args),
        FXBrokerFly(strike=["-10d", "atm_delta", "10d"], **option_args),
    ],
    s=[6.314, 2.219, -220,
       4.815, 0.475, 0.788, 0.226, 0.466
       ],
    fx=fxf,
)
#fig, ax, line = smile.plot()
#plt.show()
#plt.close()


#print("smile.nodes")
#print(smile.nodes)

target_deltas = [0.05, 0.15, 0.35]

print(smile)

for delta, vol in smile.nodes.items():
    print(f"Delta {delta}: {vol.real}")

smile.csolve()

delta_p_spot = smile.get(target_deltas[1], "spot", -1)
print(f"\nspot target_deltas {target_deltas[1]} here: {delta_p_spot}")
'''
for i in range(len(target_deltas)):
    delta_p_spot = smile.get(target_deltas[i], "spot", -1)
    print(f"\nspot target_deltas {target_deltas[i]} here: {delta_p_spot}")
'''
    #delta_p_fwd = smile.get(target_deltas[i], "forward", -1)
    #print(f"\nfwd target_deltas {target_deltas[i]} here: {delta_p_fwd}")