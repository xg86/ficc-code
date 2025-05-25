import QuantLib as ql

# 1. Market Data for USD/CNY
spot = 7.2256  # Spot FX rate (USD/CNY)
strike = 7.1  # Strike price
barrier = 7.2959  # Barrier level
usd_rate = 4.06303/100  # USD risk-free rate
cny_rate = 1.22546/100  # CNY risk-free rate
volatility = 4.683/100  # FX volatility (8%)
expiry = 1.0  # 1 year to expiry
rebate = 0  # Rebate in CNY (Cash-Or-Nothing equivalent)
h = 0.01  # Small bump for finite difference

# 2. Set Evaluation Date
today = ql.Date(18, 3,2025)
ql.Settings.instance().evaluationDate = today
#maturity = today + ql.Period(int(expiry * 365), ql.Days)
maturity = ql.Date(18, 3,2026)

# 3. Define Payoff (Use PlainVanillaPayoff Instead)
payoff = ql.PlainVanillaPayoff(ql.Option.Call, strike)

# 4. Define Barrier Option (With Rebate)
barrier_type = ql.Barrier.UpOut  # Knock-out if price crosses above barrier
exercise = ql.EuropeanExercise(maturity)
barrier_option = ql.BarrierOption(barrier_type, barrier, rebate, payoff, exercise)


# 5. Function to Price the Barrier Option
def price_barrier_option(spot_price, vol):
    # Spot Handle
    spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))

    # Yield Curves
    usd_curve = ql.YieldTermStructureHandle(
        ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(usd_rate)), ql.Actual365Fixed())
    )
    cny_curve = ql.YieldTermStructureHandle(
        ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(cny_rate)), ql.Actual365Fixed())
    )
    vol_handle = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(today, ql.NullCalendar(), ql.QuoteHandle(ql.SimpleQuote(vol)), ql.Actual365Fixed())
    )

    # Black-Scholes Process
    bsm_process = ql.BlackScholesProcess(spot_handle, cny_curve, vol_handle)

    # Pricing Engine
    engine = ql.AnalyticBarrierEngine(bsm_process)
    barrier_option.setPricingEngine(engine)

    # Compute Price
    return barrier_option.NPV()


# 6. Compute Greeks Using Finite Difference Method
V = price_barrier_option(spot, volatility)  # Base Price
V_plus = price_barrier_option(spot + h, volatility)  # Spot Up
V_minus = price_barrier_option(spot - h, volatility)  # Spot Down
V_vega_plus = price_barrier_option(spot, volatility + h)  # Volatility Up
V_vega_minus = price_barrier_option(spot, volatility - h)  # Volatility Down

delta = (V_plus - V_minus) / (2 * h)  # Central Difference
gamma = (V_plus - 2 * V + V_minus) / (h ** 2)  # Second Derivative
vega = (V_vega_plus - V_vega_minus) / (2 * h)  # Volatility Sensitivity

# 7. Print Results
print(f"USD/CNY Barrier FX Option Price1: {barrier_option.NPV():.4f} CNY")
print(f"USD/CNY Barrier FX Option Price: {V:.4f} CNY")
print(f"Delta: {delta:.4f}")
print(f"Gamma: {gamma:.4f}")
print(f"Vega: {vega:.4f} CNY")
