# This is the 'SABR-solution'... fit a SABR smile to each tenor, and let the vol surface interpolate
# between them. Below, we're using the python minimizer to do a fit to the provided smiles

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import norm
from scipy import optimize, stats
import QuantLib as ql
from mpl_toolkits.mplot3d import Axes3D  # Import this explicitly

calc_date = ql.Date(1, 9, 2020)

def plot_vol_surface(vol_surface, plot_years=np.arange(0.1, 3, 0.1), plot_strikes=np.arange(70, 130, 1), funct='blackVol'):
    if type(vol_surface) != list:
        surfaces = [vol_surface]
    else:
        surfaces = vol_surface

    fig = plt.figure(figsize=(10, 6))
    #ax = fig.gca(projection='3d')
    ax = plt.axes(projection='3d')
    X, Y = np.meshgrid(plot_strikes, plot_years)
    Z_array, Z_min, Z_max = [], 100, 0

    for surface in surfaces:
        method_to_call = getattr(surface, funct)

        Z = np.array([method_to_call(float(y), float(x))
                      for xr, yr in zip(X, Y)
                          for x, y in zip(xr, yr)]
                     ).reshape(len(X), len(X[0]))

        Z_array.append(Z)
        Z_min, Z_max = min(Z_min, Z.min()), max(Z_max, Z.max())

    # In case of multiple surfaces, need to find universal max and min first for colourmap
    for Z in Z_array:
        N = (Z - Z_min) / (Z_max - Z_min)  # normalize 0 -> 1 for the colormap
        surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0.1, facecolors=cm.coolwarm(N))

    m = cm.ScalarMappable(cmap=cm.coolwarm)
    m.set_array(Z)
    plt.colorbar(m, shrink=0.8, aspect=20)
    ax.view_init(30, 300)

def generate_multi_paths_df(process, num_paths=1000, timestep=24, length=2):
    """Generates multiple paths from an n-factor process, each factor is returned in a seperate df"""
    times = ql.TimeGrid(length, timestep)
    dimension = process.factors()

    rng = ql.GaussianRandomSequenceGenerator(ql.UniformRandomSequenceGenerator(dimension * timestep, ql.UniformRandomGenerator()))
    seq = ql.GaussianMultiPathGenerator(process, list(times), rng, False)

    paths = [[] for i in range(dimension)]

    for i in range(num_paths):
        sample_path = seq.next()
        values = sample_path.value()
        spot = values[0]

        for j in range(dimension):
            paths[j].append([x for x in values[j]])

    df_paths = [pd.DataFrame(path, columns=[spot.time(x) for x in range(len(spot))]) for path in paths]

    return df_paths

# Define functions to map from delta to strike
def strike_from_spot_delta(tte, fwd, vol, delta, dcf_for, put_call):
    sigma_root_t = vol * np.sqrt(tte)
    inv_norm = norm.ppf(delta * put_call * dcf_for)

    return fwd * np.exp(-sigma_root_t * put_call * inv_norm + 0.5 * sigma_root_t * sigma_root_t)

def strike_from_fwd_delta(tte, fwd, vol, delta, put_call):
    sigma_root_t = vol * np.sqrt(tte)
    inv_norm = norm.ppf(delta * put_call)

    return fwd * np.exp(-sigma_root_t * put_call * inv_norm + 0.5 * sigma_root_t * sigma_root_t)

# World State for Vanilla Pricing
spot = 1.17858
rateDom = 0.0
rateFor = 0.0
calendar = ql.NullCalendar()
day_count = ql.Actual365Fixed()

# Set up the flat risk-free curves
riskFreeCurveDom = ql.FlatForward(calc_date, rateDom, ql.Actual365Fixed())
riskFreeCurveFor = ql.FlatForward(calc_date, rateFor, ql.Actual365Fixed())

dom_dcf_curve = ql.YieldTermStructureHandle(riskFreeCurveDom)
for_dcf_curve = ql.YieldTermStructureHandle(riskFreeCurveFor)

tenors = ['1W', '2W', '1M', '2M', '3M', '6M', '9M', '1Y', '18M', '2Y']
deltas = ['ATM', '35D Call EUR', '35D Put EUR', '25D Call EUR', '25D Put EUR', '15D Call EUR', '15D Put EUR', '10D Call EUR', '10D Put EUR', '5D Call EUR', '5D Put EUR']
vols = [[7.255, 7.428, 7.193, 7.61, 7.205, 7.864, 7.261, 8.033, 7.318, 8.299, 7.426],
        [7.14, 7.335, 7.07, 7.54, 7.08, 7.836, 7.149, 8.032, 7.217, 8.34, 7.344],
        [7.195, 7.4, 7.13, 7.637, 7.167, 7.984, 7.286, 8.226, 7.394, 8.597, 7.58],
        [7.17, 7.39, 7.11, 7.645, 7.155, 8.031, 7.304, 8.303, 7.438, 8.715, 7.661],
        [7.6, 7.827, 7.547, 8.105, 7.615, 8.539, 7.796, 8.847, 7.952, 9.308, 8.222],
        [7.285, 7.54, 7.26, 7.878, 7.383, 8.434, 7.671, 8.845, 7.925, 9.439, 8.344],
        [7.27, 7.537, 7.262, 7.915, 7.425, 8.576, 7.819, 9.078, 8.162, 9.77, 8.713],
        [7.275, 7.54, 7.275, 7.935, 7.455, 8.644, 7.891, 9.188, 8.283, 9.922, 8.898],
        [7.487, 7.724, 7.521, 8.089, 7.731, 8.742, 8.197, 9.242, 8.592, 9.943, 9.232],
        [7.59, 7.81, 7.645, 8.166, 7.874, 8.837, 8.382, 9.354, 8.816, 10.065, 9.51]]

# Convert vol surface to strike surface (we need both)
full_option_surface = []

for i, name in enumerate(deltas):
    delta = 0.5 if name == "ATM" else int(name.split(" ")[0].replace("D", "")) / 100.
    put_call = 1 if name == "ATM" else -1 if name.split(" ")[1] == "Put" else 1

    for j, tenor in enumerate(tenors):
        expiry = calc_date + ql.Period(tenor)

        tte = day_count.yearFraction(calc_date, expiry)
        fwd = spot * for_dcf_curve.discount(expiry) / dom_dcf_curve.discount(expiry)
        for_dcf = for_dcf_curve.discount(expiry)
        vol = vols[j][i] / 100.

        # Assume that spot delta used out to 1Y (used to be this way...)
        if tte < 1.:
            strike = strike_from_spot_delta(tte, fwd, vol, put_call*delta, for_dcf, put_call)
        else:
            strike = strike_from_fwd_delta(tte, fwd, vol, put_call*delta, put_call)

        full_option_surface.append({"vol": vol,
                                    "fwd": fwd,
                                    "expiry": tenor,
                                    "tte": tte,
                                    "delta": put_call*delta,
                                    "strike": strike,
                                    "put_call": put_call,
                                    "for_dcf": for_dcf,
                                    "name": name})

full_df = pd.DataFrame(full_option_surface)

display_df = full_df.copy()
display_df['call_delta'] = 1 - (display_df['put_call'].clip(0) - display_df['delta'])

df = display_df.set_index(['tte', 'call_delta']).sort_index()[['strike']].unstack()
df = df.reindex(sorted(df.columns, reverse=True), axis=1)

fig = plt.figure(figsize=(12,9))

plt.subplot(2,1,1)

plt.plot(full_df['tte'], full_df['strike'], marker='o', linestyle='none', label='strike grid')

plt.title("Option Strike Grid, tte vs. K")
plt.grid()
plt.xlim(0, 2.1)
plt.show()



df_params = pd.read_csv('sabr_parameters.csv')
print(df_params)
calibrated_params = {}

# Fit a local vol surface to a strike-tenor grid extrapolated according to SABR
strikes = np.linspace(1.0, 1.5, 21)
expiration_dates = [calc_date + ql.Period(int(365 * x), ql.Days) for x in df_params.tte]

implied_vols = []
for index, row in df_params.iterrows():
    tte, fwd, v0, beta, alpha, rho = row['tte'], row['fwd'], row['v0'], row['beta'], row['alpha'], row['rho']
    vols = [ql.sabrVolatility(strike, fwd, tte, v0, beta, alpha, rho) for strike in strikes]
    implied_vols.append(vols)

implied_vols = ql.Matrix(np.matrix(implied_vols).transpose().tolist())

local_vol_surface = ql.BlackVarianceSurface(calc_date, calendar, expiration_dates, strikes, implied_vols, day_count)

# Calculate the Dupire instantaneous vol surface
local_vol_surface.setInterpolation('bicubic')
local_vol_handle = ql.BlackVolTermStructureHandle(local_vol_surface)
local_vol = ql.LocalVolSurface(local_vol_handle, dom_dcf_curve, for_dcf_curve, ql.QuoteHandle(ql.SimpleQuote(spot)))

# Calibrating a leverage function
end_date = ql.Date(21, 9, 2021)
generator_factory = ql.MTBrownianGeneratorFactory(43)

timeStepsPerYear = 182
nBins = 101
calibrationPaths = 2**19


# Fit a Heston model to the data as well
v0 = 0.005;
kappa = 0.01;
theta = 0.0064;
rho = 0.0;
sigma = 0.01

heston_process = ql.HestonProcess(dom_dcf_curve, for_dcf_curve, ql.QuoteHandle(ql.SimpleQuote(spot)), v0, kappa, theta,
                                  sigma, rho)
heston_model = ql.HestonModel(heston_process)


stoch_local_mc_model = ql.HestonSLVMCModel(local_vol, heston_model, generator_factory, end_date, timeStepsPerYear, nBins, calibrationPaths)

leverage_functon = stoch_local_mc_model.leverageFunction()

plot_vol_surface(leverage_functon, funct='localVol', plot_years=np.arange(0.5, 0.98, 0.1), plot_strikes=np.linspace(1.05, 1.35, 20))

plt.show()