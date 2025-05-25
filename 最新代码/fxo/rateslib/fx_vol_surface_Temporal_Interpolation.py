from rateslib import *
from pandas import Series
import matplotlib.pyplot as plt

#FX Volatility Surface Temporal Interpolation
fxvs = FXDeltaVolSurface(
    expiries=[
        dt(2024, 2, 12), # Spot
        dt(2024, 2, 16), # 1W
        dt(2024, 2, 23), # 2W
        dt(2024, 3, 1), # 3W
        dt(2024, 3, 8), # 4W
    ],
    #delta_indexes=[0.5],
    delta_indexes=[0.5, 0.25, 0.15],
    node_values=[[8.15], [11.95], [11.97], [11.75], [11.80]],
    eval_date=dt(2024, 2, 9),
    delta_type="forward",
)

fig, ax, plt = fxvs.plot()
plt.show()

cal = get_calendar("all")
x, y = [], []
for date in cal.cal_date_range(dt(2024, 2, 10), dt(2024, 3, 8)):
    x.append(date)
    smile = fxvs.get_smile(date)
    node = smile.nodes[0.5]
    d25 = smile.get(0.25, "forward", -1)
    print(f"\nfwd target_deltas 0.25 here: {d25}")
    d15 = smile.get(0.15, "forward", -1)
    print(f"\nfwd target_deltas 0.15 here: {d15}")
    #y.append(fxvs.get_smile(date).nodes[0.5])
    y.append(node)

fig, ax = plt.subplots(1,1)
plt.xticks(rotation=90)
ax.plot(x,y)
plt.show()

cal = get_calendar("bus")
weekends = [
    _  for _ in cal.cal_date_range(dt(2024, 2, 9), dt(2024, 3, 11))
    if _ not in cal.bus_date_range(dt(2024, 2, 9), dt(2024, 3, 11))
]
weights = Series(0.0, index=weekends)

print(f"\nweights here: {weights}")


