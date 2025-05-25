import QuantLib as ql

# 1. Market Data (for USD/CNY)
spot = 7.2256  # Spot FX rate (USD/CNY)
strike = 7.2959  # Strike price
usd_rate = 4.06303/100  # USD risk-free rate (domestic)
cny_rate = 1.22546/100  # CNY risk-free rate (foreign)
volatility = 5.4249/100  # FX volatility (8%)
expiry = 1.0  # 1 year to expiry

'''
EvaluationDate = ql.Date(3, 1,2022)
SettlementDate = ql.Date(5, 1, 2022) #Evaluation +2
ExpiryDate = ql.Date(10, 1, 2022) #Evaluation + term which is 1 week
DeliveryDate = ql.Date(12, 1, 2022) #Expiry +2
'''
# 2. Set Evaluation Date
today = ql.Date(18, 3,2025)
ql.Settings.instance().evaluationDate = today
#maturity = today + ql.Period(int(expiry * 365), ql.Days)
maturity = ql.Date(18, 3,2026)


# 3. Payoff Definition (Cash-or-Nothing)
payout_cny = 1_000_000 # Cash payout in CNY if ITM
payoff = ql.CashOrNothingPayoff(ql.Option.Call, strike, payout_cny)

# 4. Define European Exercise
exercise = ql.EuropeanExercise(maturity)

# 5. Construct the Digital FX Option
option = ql.VanillaOption(payoff, exercise)

# 6. Build the Black-Scholes-Merton Process for USD/CNY
spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot))
usd_curve = ql.YieldTermStructureHandle(
    ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(usd_rate)), ql.Actual365Fixed())
)
cny_curve = ql.YieldTermStructureHandle(
    ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(cny_rate)), ql.Actual365Fixed())
)
vol_handle = ql.BlackVolTermStructureHandle(
    ql.BlackConstantVol(today, ql.NullCalendar(), ql.QuoteHandle(ql.SimpleQuote(volatility)), ql.Actual365Fixed())
)

# 7. Black-Scholes-Merton Engine Setup
bsm_process = ql.BlackScholesProcess(spot_handle, cny_curve, vol_handle)
engine = ql.AnalyticEuropeanEngine(bsm_process)

# 8. Price the Option
option.setPricingEngine(engine)

# 9. Compute Greeks
npv = option.NPV()  # Option price in CNY
forward_delta = option.delta()  # Forward Delta as percentage
vega = option.vega()  # Vega in CNY (per 1% vol change)
gamma = option.gamma()  # Gamma in CNY

# 10. Print Results
print(f"USD/CNY Digital FX Option Price: {npv:.4f} CNY")
print(f"Forward Delta: {forward_delta:.4f}")
print(f"Vega (CNY): {vega:.4f} CNY")
print(f"Gamma (CNY): {gamma:.4f} CNY")


npv_usd = npv * usd_curve.discount(maturity)

print(f"Discounted Price in USD: {npv_usd:.4f} USD (if needed)")