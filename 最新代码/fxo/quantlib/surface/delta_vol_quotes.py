#from market import curveinfo
import QuantLib as ql
import numpy as np
import pandas as pd
#https://quant.stackexchange.com/questions/57376/interpolation-of-fx-vol-surface-from-non-uniform-strike-vs-tenor-grid/57383#57383
def delta_vol_quotes(ccypair,fxcurve):

    sheetname = ccypair + '_fx_volcurve'

    df = pd.read_excel('~/iCloud/python_stuff/finance/marketdata.xlsx', sheet_name=sheetname)

    curveinfo = curveinfo(ccypair, 'fxvols')

    calendar = curveinfo.loc['calendar', 'fxvols']

    daycount = curveinfo.loc['curve_daycount', 'fxvols']

    settlement = curveinfo.loc['curve_sett', 'fxvols']

    flat_vol = ql.SimpleQuote(curveinfo.loc['flat_vol', 'fxvols'])

    flat_vol_shift = ql.SimpleQuote(0)

    used_flat_vol = ql.CompositeQuote(ql.QuoteHandle(flat_vol_shift), ql.QuoteHandle(flat_vol), f)

    vol_shift = ql.SimpleQuote(0)

    calculation_date = fxcurve.referenceDate()

    settdate = calendar.advance(calculation_date, settlement, ql.Days)

    date_periods = df[ccypair].tolist()
    atm = [ql.CompositeQuote(ql.QuoteHandle(vol_shift), ql.QuoteHandle(ql.SimpleQuote(i)), f) for i in
           df['ATM'].tolist()]
    C25 = [ql.CompositeQuote(ql.QuoteHandle(vol_shift), ql.QuoteHandle(ql.SimpleQuote(i)), f) for i in
           df['25C'].tolist()]
    P25 = [ql.CompositeQuote(ql.QuoteHandle(vol_shift), ql.QuoteHandle(ql.SimpleQuote(i)), f) for i in
           df['25P'].tolist()]
    C10 = [ql.CompositeQuote(ql.QuoteHandle(vol_shift), ql.QuoteHandle(ql.SimpleQuote(i)), f) for i in
           df['10C'].tolist()]
    P10 = [ql.CompositeQuote(ql.QuoteHandle(vol_shift), ql.QuoteHandle(ql.SimpleQuote(i)), f) for i in
           df['10P'].tolist()]

    dates = [calendar.advance(settdate, ql.Period(i)) for i in date_periods]

    yearfracs = [daycount.yearFraction(settdate, i) for i in dates]

    dvq_C25 = [ql.DeltaVolQuote(0.25, ql.QuoteHandle(i), j, 0) for i, j in zip(C25, yearfracs)]
    dvq_P25 = [ql.DeltaVolQuote(-0.25, ql.QuoteHandle(i), j, 0) for i, j in zip(P25, yearfracs)]
    dvq_C10 = [ql.DeltaVolQuote(0.10, ql.QuoteHandle(i), j, 0) for i, j in zip(C10, yearfracs)]
    dvq_P10 = [ql.DeltaVolQuote(-0.10, ql.QuoteHandle(i), j, 0) for i, j in zip(P10, yearfracs)]

    info=[settdate,
          calendar,
          daycount,
          df,
          used_flat_vol,
          vol_shift,
          flat_vol_shift,
          date_periods]


    return atm,dvq_C25,dvq_P25,dvq_C10,dvq_P10,dates,yearfracs,info

def fxvolsurface(ccypair,FX,fxcurve,curve):

    atm,dvq_C25,dvq_P25,dvq_C10,dvq_P10,dates,yearfracs,info = delta_vol_quotes(ccypair,fxcurve)

    settdate = info[0]
    calendar=info[1]
    daycount=info[2]
    df=info[3]
    used_flat_vol=info[4]
    vol_shift=info[5]
    flat_vol_shift=info[6]
    date_periods=info[7]

    blackdc_C25=[ql.BlackDeltaCalculator(ql.Option.Call,
                                         j.Spot,
                                         FX.value(),
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

    hestonstrikes=[P10_strikes,
                   P25_strikes,
                   ATM_strikes,
                   C25_strikes,
                   C10_strikes]

    hestonvoldata=[df['10P'].tolist(),
                   df['25P'].tolist(),
                   df['ATM'].tolist(),
                   df['25C'].tolist(),
                   df['10C'].tolist()]

    volmatrix=[]
    for i in range(0,len(atm)):
        volsurface=ql.BlackVolTermStructureHandle(
            ql.BlackVarianceSurface(settdate,
                                    calendar,
                                    [dates[i]],
                                    [P10_strikes[i],
                                     P25_strikes[i],
                                     ATM_strikes[i],
                                     C25_strikes[i],
                                     C10_strikes[i]
                                     ],
                                    [[dvq_P10[i].value()],
                                     [dvq_P25[i].value()],
                                     [atm[i].value()],
                                     [dvq_C25[i].value()],
                                     [dvq_C10[i].value()]
                                     ],
                                    daycount)
        )
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

    fxvoldata=pd.DataFrame({'10P strike':P10_strikes,
                            '25P strike':P25_strikes,
                            'ATM strike':ATM_strikes,
                            '25C strike':C25_strikes,
                            '10C strike':C10_strikes,
                            '10P vol':df['10P'].tolist(),
                            '25P vol':df['25P'].tolist(),
                            'ATM vol':df['ATM'].tolist(),
                            '25C vol':df['25C'].tolist(),
                            '10C vol':df['10C'].tolist()})

    fxvoldata.index=date_periods

    fxvolsdf=pd.DataFrame({'fxvolsurface':[fxvolsurface,
                                           flatfxvolsurface],
                           'fxvoldata':[fxvoldata,None]})

    fxvolsdf.index=['surface','flat']

    fxvolshiftsdf=pd.DataFrame({'fxvolshifts':[vol_shift,
                                               flat_vol_shift]})
    fxvolshiftsdf.index=['surface','flat']

    return fxvolshiftsdf,fxvolsdf