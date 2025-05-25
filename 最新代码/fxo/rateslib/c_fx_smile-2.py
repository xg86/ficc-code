from rateslib.fx_volatility import FXDeltaVolSmile
from datetime import datetime as dt
from matplotlib import pyplot as plt
smile = FXDeltaVolSmile(
    eval_date=dt(2000, 1, 1),
    expiry=dt(2000, 7, 1),
    nodes={
        0.25: 10.3,
        0.5: 9.1,
        0.75: 10.8
    },
    delta_type="forward"
)
fig, ax, lines = smile.plot(x_axis="moneyness")
plt.show()
plt.close()