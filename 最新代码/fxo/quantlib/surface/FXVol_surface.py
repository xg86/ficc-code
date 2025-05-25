import QuantLib as ql
import numpy as np
import matplotlib.pyplot as plt

#https://quant.stackexchange.com/questions/57376/interpolation-of-fx-vol-surface-from-non-uniform-strike-vs-tenor-grid/57383#57383
def fxvolsurface(ccypair,FX,fxcurve,curve):

    atm,dvq_C25,dvq_P25,dvq_C10,dvq_P10,dates,yearfracs,info = deltavolquotes(ccypair,fxcurve)
    settdate = info[0]
    calendar=info[1]
    daycount=info[2]
    df=info[3]
    used_flat_vol=info[4]
    vol_shift=info[5]
    flat_vol_shift=info[6]
    date_periods=info[7]

    blackdc_C25=[ql.BlackDeltaCalculator(ql.Option.Call,j.Spot,FX.value(),
                                       fxcurve.discount(i)/fxcurve.discount(settdate),
                                       curve.discount(i)/curve.discount(settdate),
                                       j.value()*(k**0.5))
                                       for i,j,k in zip(dates,dvq_C25,yearfracs)]
    blackdc_C10=[ql.BlackDeltaCalculator(ql.Option.Call,j.Spot,FX.value(),
                                       fxcurve.discount(i)/fxcurve.discount(settdate),
                                       curve.discount(i)/curve.discount(settdate),
                                       j.value()*(k**0.5))
                                       for i,j,k in zip(dates,dvq_C10,yearfracs)]
    blackdc_P25=[ql.BlackDeltaCalculator(ql.Option.Put,j.Spot,FX.value(),
                                       fxcurve.discount(i)/fxcurve.discount(settdate),
                                       curve.discount(i)/curve.discount(settdate),
                                       j.value()*(k**0.5))
                                       for i,j,k in zip(dates,dvq_P25,yearfracs)]
    blackdc_P10=[ql.BlackDeltaCalculator(ql.Option.Put,j.Spot,FX.value(),
                                       fxcurve.discount(i)/fxcurve.discount(settdate),
                                       curve.discount(i)/curve.discount(settdate),
                                       j.value()*(k**0.5))
                                       for i,j,k in zip(dates,dvq_P10,yearfracs)]
    C25_strikes=[i.strikeFromDelta(0.25) for i in blackdc_C25]
    C10_strikes=[i.strikeFromDelta(0.10) for i in blackdc_C10]
    P25_strikes=[i.strikeFromDelta(-0.25) for i in blackdc_P25]
    P10_strikes=[i.strikeFromDelta(-0.10) for i in blackdc_P10]
    ATM_strikes=[i.atmStrike(j.AtmFwd) for i,j in zip(blackdc_C25,dvq_C25)]
    strikeset=ATM_strikes+C25_strikes+C10_strikes+P25_strikes+P10_strikes
    strikeset.sort()
    hestonstrikes=[P10_strikes,P25_strikes,ATM_strikes,C25_strikes,C10_strikes]
    hestonvoldata=[df['10P'].tolist(),df['25P'].tolist(),df['ATM'].tolist(),df['25C'].tolist(),df['10C'].tolist()]

    volmatrix=[]
    for i in range(0,len(atm)):
        volsurface=ql.BlackVolTermStructureHandle(ql.BlackVarianceSurface(settdate,calendar,[dates[i]],
                                    [P10_strikes[i],P25_strikes[i],ATM_strikes[i],C25_strikes[i],C10_strikes[i]],
                                    [[dvq_P10[i].value()],[dvq_P25[i].value()],[atm[i].value()],[dvq_C25[i].value()],
                                     [dvq_C10[i].value()]],
                                    daycount))
        volmatrix.append([volsurface.blackVol(dates[i],j,True) for j in strikeset])
    volarray=np.array(volmatrix).transpose()
    matrix = []
    for i in range(0, volarray.shape[0]):
        matrix.append(volarray[i].tolist())
    fxvolsurface=ql.BlackVolTermStructureHandle(
        ql.BlackVarianceSurface(settdate,calendar,dates,strikeset,matrix,daycount))

    '''
    process = ql.HestonProcess(fxcurve, curve, ql.QuoteHandle(FX), 0.01, 0.5, 0.01, 0.1, 0)
    model = ql.HestonModel(process)
    engine = ql.AnalyticHestonEngine(model)
    print(model.params())
    hmh = []
    for i in range(0,len(date_periods)):
        for j in range(0,len(hestonstrikes)):
            helper=ql.HestonModelHelper(ql.Period(date_periods[i]), calendar, FX.value(),hestonstrikes[j][i],
                                        ql.QuoteHandle(ql.SimpleQuote(hestonvoldata[j][i])),fxcurve,curve)
            helper.setPricingEngine(engine)
            hmh.append(helper)
    lm = ql.LevenbergMarquardt()
    model.calibrate(hmh, lm,ql.EndCriteria(500, 10, 1.0e-8, 1.0e-8, 1.0e-8))
    vs = ql.BlackVolTermStructureHandle(ql.HestonBlackVolSurface(ql.HestonModelHandle(model)))
    vs.enableExtrapolation()'''

    flatfxvolsurface = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(settdate, calendar, ql.QuoteHandle(used_flat_vol), daycount))

    fxvoldata=pd.DataFrame({'10P strike':P10_strikes,'25P strike':P25_strikes,'ATM strike':ATM_strikes,
                            '25C strike':C25_strikes,'10C strike':C10_strikes,'10P vol':df['10P'].tolist(),
                            '25P vol':df['25P'].tolist(),'ATM vol':df['ATM'].tolist(),
                            '25C vol':df['25C'].tolist(),'10C vol':df['10C'].tolist()})
    fxvoldata.index=date_periods

    fxvolsdf=pd.DataFrame({'fxvolsurface':[fxvolsurface,flatfxvolsurface],'fxvoldata':[fxvoldata,None]})
    fxvolsdf.index=['surface','flat']
    fxvolshiftsdf=pd.DataFrame({'fxvolshifts':[vol_shift,flat_vol_shift]})
    fxvolshiftsdf.index=['surface','flat']

    return fxvolshiftsdf,fxvolsdf

# This is the 'SABR-solution'... fit a SABR smile to each tenor, and let the vol surface interpolate
# between them. Below, we're using the python minimizer to do a fit to the provided smiles

calibrated_params = {}

# params are sigma_0, beta, vol_vol, rho
params = [0.4, 0.6, 0.1, 0.2]

fig, i = plt.figure(figsize=(6, 42)), 1

for tte, group in full_df.groupby('tte'):
    fwd = group.iloc[0]['fwd']
    expiry = group.iloc[0]['expiry']
    strikes = group.sort_values('strike')['strike'].values
    vols = group.sort_values('strike')['vol'].values

    def f(params):
        params[0] = max(params[0], 1e-8) # Avoid alpha going negative
        params[1] = max(params[1], 1e-8) # Avoid beta going negative
        params[2] = max(params[2], 1e-8) # Avoid nu going negative
        params[3] = max(params[3], -0.999) # Avoid nu going negative
        params[3] = min(params[3], 0.999) # Avoid nu going negative

        calc_vols = np.array([
            ql.sabrVolatility(strike, fwd, tte, *params)
            for strike in strikes
        ])
        error = ((calc_vols - np.array(vols))**2 ).mean() **.5
        return error

    cons = (
        {'type': 'ineq', 'fun': lambda x: x[0]},
        {'type': 'ineq', 'fun': lambda x: 0.99 - x[1]},
        {'type': 'ineq', 'fun': lambda x: x[1]},
        {'type': 'ineq', 'fun': lambda x: x[2]},
        {'type': 'ineq', 'fun': lambda x: 1. - x[3]**2}
    )

    result = optimize.minimize(f, params, constraints=cons, options={'eps': 1e-5})
    new_params = result['x']

    calibrated_params[tte] = {'v0': new_params[0], 'beta': new_params[1], 'alpha': new_params[2], 'rho': new_params[3], 'fwd': fwd}

    newVols = [ql.sabrVolatility(strike, fwd, tte, *new_params) for strike in strikes]

    # Start next round of optimisation with this round's parameters, they're probably quite close!
    params = new_params

    plt.subplot(len(tenors), 1, i)
    i = i+1

    plt.plot(strikes, vols, marker='o', linestyle='none', label='market {}'.format(expiry))
    plt.plot(strikes, newVols, label='SABR {0:1.2f}'.format(tte))
    plt.title("Smile {0:1.3f}".format(tte))

    plt.grid()
    plt.legend()

plt.show()

# Fit a local vol surface to a strike-tenor grid extrapolated according to SABR
strikes = np.linspace(1.0, 1.5, 21)
expiration_dates = [calc_date + ql.Period(int(365 * x), ql.Days) for x in params.index]

implied_vols = []
for tte, row in params.iterrows():
    fwd, v0, beta, alpha, rho = row['fwd'], row['v0'], row['beta'], row['alpha'], row['rho']
    vols = [ql.sabrVolatility(strike, fwd, tte, v0, beta, alpha, rho) for strike in strikes]
    implied_vols.append(vols)

implied_vols = ql.Matrix(np.matrix(implied_vols).transpose().tolist())

local_vol_surface = ql.BlackVarianceSurface(calc_date, calendar, expiration_dates, strikes, implied_vols, day_count)

# Fit a Heston model to the data as well
v0 = 0.005;
kappa = 0.01;
theta = 0.0064;
rho = 0.0;
sigma = 0.01

heston_process = ql.HestonProcess(dom_dcf_curve, for_dcf_curve, ql.QuoteHandle(ql.SimpleQuote(spot)), v0, kappa, theta,
                                  sigma, rho)
heston_model = ql.HestonModel(heston_process)
heston_engine = ql.AnalyticHestonEngine(heston_model)

# Set up Heston 'helpers' to calibrate to
heston_helpers = []

for idx, row in full_df.iterrows():
    vol = row['vol']
    strike = row['strike']
    tenor = ql.Period(row['expiry'])

    helper = ql.HestonModelHelper(tenor, calendar, spot, strike, ql.QuoteHandle(ql.SimpleQuote(vol)), dom_dcf_curve,
                                  for_dcf_curve)
    helper.setPricingEngine(heston_engine)
    heston_helpers.append(helper)

lm = ql.LevenbergMarquardt(1e-8, 1e-8, 1e-8)
heston_model.calibrate(heston_helpers, lm, ql.EndCriteria(5000, 100, 1.0e-8, 1.0e-8, 1.0e-8))
theta, kappa, sigma, rho, v0 = heston_model.params()
feller = 2 * kappa * theta - sigma ** 2

print(
    f"theta = {theta:.4f}, kappa = {kappa:.4f}, sigma = {sigma:.4f}, rho = {rho:.4f}, v0 = {v0:.4f}, spot = {spot:.4f}, feller = {feller:.4f}")

heston_handle = ql.HestonModelHandle(heston_model)
heston_vol_surface = ql.HestonBlackVolSurface(heston_handle)

# Plot the two vol surfaces ...
plot_vol_surface([local_vol_surface, heston_vol_surface], plot_years=np.arange(0.1, 1.0, 0.1),
                 plot_strikes=np.linspace(1.05, 1.45, 20))



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

stoch_local_mc_model = ql.HestonSLVMCModel(local_vol, heston_model, generator_factory, end_date, timeStepsPerYear, nBins, calibrationPaths)

leverage_functon = stoch_local_mc_model.leverageFunction()

plot_vol_surface(leverage_functon, funct='localVol', plot_years=np.arange(0.5, 0.98, 0.1), plot_strikes=np.linspace(1.05, 1.35, 20))

