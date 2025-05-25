import QuantLib as ql


Spot = 1.1
Strike = 1.101
Sigma = 10/100 #Vol
Ccy1Rate = 5/100 #eur DEPO
Ccy2Rate = 10/100 #usd DEPO
OptionType = ql.Option.Call

#Option dates in quantlib objects
EvaluationDate = ql.Date(3, 1,2022)
SettlementDate = ql.Date(5, 1, 2022) #Evaluation +2
ExpiryDate = ql.Date(10, 1, 2022) #Evaluation + term which is 1 week
DeliveryDate = ql.Date(12, 1, 2022) #Expiry +2
NumberOfDaysBetween = ExpiryDate - EvaluationDate
#print(NumberOfDaysBetween)

#Generate continuous interest rates
EurRate = Ccy1Rate
UsdRate = Ccy2Rate

#Create QuoteHandle objects. Easily to adapt later on.
#You can only access SimpleQuote objects. When you use setvalue, you can change it.
#These global variables will then be used in pricing the option.
#Everything will be adaptable except for the strike.
SpotGlobal = ql.SimpleQuote(Spot)
SpotHandle = ql.QuoteHandle(SpotGlobal)
VolGlobal = ql.SimpleQuote(Sigma)
VolHandle = ql.QuoteHandle(VolGlobal)
UsdRateGlobal = ql.SimpleQuote(UsdRate)
UsdRateHandle = ql.QuoteHandle(UsdRateGlobal)
EurRateGlobal = ql.SimpleQuote(EurRate)
EurRateHandle = ql.QuoteHandle(EurRateGlobal)

#Settings such as calendar, evaluationdate; daycount
Calendar = ql.UnitedStates(ql.UnitedStates.Settlement)
ql.Settings.instance().evaluationDate = EvaluationDate
DayCountRate = ql.Actual360()
DayCountVolatility = ql.ActualActual(ql.ActualActual.ISDA)

#Create rate curves, vol surface and GK process
RiskFreeRateEUR = ql.YieldTermStructureHandle(ql.FlatForward(0, Calendar, EurRateHandle, DayCountRate))
RiskFreeRateUSD = ql.YieldTermStructureHandle(ql.FlatForward(0, Calendar, UsdRate, DayCountRate))
Volatility = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(0, Calendar, VolHandle, DayCountVolatility))
GKProcess = ql.GarmanKohlagenProcess(SpotHandle, RiskFreeRateEUR, RiskFreeRateUSD, Volatility)

#Generate option
Payoff = ql.PlainVanillaPayoff(OptionType, Strike)
Exercise = ql.EuropeanExercise(ExpiryDate)
Option = ql.VanillaOption(Payoff, Exercise)
Option.setPricingEngine(ql.AnalyticEuropeanEngine(GKProcess))
BsPrice = Option.NPV()



ql.Settings.instance().evaluationDate = EvaluationDate
print("Premium EUR is:", Option.NPV()*1000000/Spot)
print("Gamma is:", Option.gamma()*1000000*Spot/100)
print("Vega is:", Option.vega()*1000000*(1/100)/Spot)
print("Theta is:", Option.theta()*1000000*(1/365)/Spot)
print("Delta is:", Option.delta()*1000000)

'''
Premium is: 5550.960519027888
Gamma is: 287777.2550015351
Vega is: 551.9015849344515
Theta is: -462.68771985750703 , BBG is 
Delta is: 504102.4957777005
'''
import numpy as np
from scipy.stats import norm


# Normal CDF function (equivalent to Julia's N(x))
def N(x):
    return norm.cdf(x)


# Given parameters
spot = 1.1
f = 1.101070
strike = 1.101
ccy1 = 0.05  # EUR
ccy2 = 0.1  # USD
vol = 0.1
days = 7

# Time calculation
t = days / 365

# Continuous rate calculations
r1_cont = np.log(1 + ccy1 * days / 360) / (days / 365)
r2_cont = np.log(1 + ccy2 * days / 360) / (days / 365)


def GKF(F, K, t, r, sigma):
    """
    Generalized Karman-Fisher option pricing function

    Args:
    F: Forward price
    K: Strike price
    t: Time to maturity
    r: Continuous risk-free rate
    sigma: Volatility

    Returns:
    Tuple of (call price, put price, d1, d2)
    """
    d1 = (np.log(F / K) + 0.5 * sigma ** 2 * t) / (sigma * np.sqrt(t))
    d2 = d1 - sigma * np.sqrt(t)

    c = np.exp(-r * t) * (F * N(d1) - K * N(d2))
    p = np.exp(-r * t) * (-F * N(-d1) + K * N(-d2))

    return c, p, d1, d2


# Calculate theta (time decay)
t1 = GKF(f, strike, days / 365, r2_cont, vol)[0] * 1000000 / spot
t2 = GKF(f, strike, (days - 1) / 365, r2_cont, vol)[0] * 1000000 / spot

theta = t2 - t1

print(f"Theta: {theta}")

