import QuantLib as ql

# FX Option parameters
spot_price = 7.12  # Spot price (USD/CNY)
strike_price = 7.75  # Strike price (USD/CNY)
maturity_in_years = 1.0  # Time to maturity in years
domestic_rate = 0.01929  # Domestic risk-free rate (CNY, in decimal form)
foreign_rate = 0.05032  # Foreign risk-free rate (must be USD, in decimal form)
volatility =6.875/100  # Implied volatility (in decimal form)
option_type = ql.Option.Call  # Call or Put option
day_count = ql.Actual365Fixed()  # Day count convention
#calendar = ql.China()  # FX market calendar (using China for example)
#calendar = ql.UnitedStates(ql.UnitedStates.Settlement)
calendar = ql.NullCalendar()

# Dates and QuantLib objects
eval_date = ql.Date(31, 10, 2024)
maturity_date = eval_date + int(365 * maturity_in_years)
exercise = ql.AmericanExercise(eval_date, maturity_date)

ql.Settings.instance().evaluationDate = eval_date
# Market data: spot price, foreign and domestic curves

spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
domestic_curve = ql.YieldTermStructureHandle(ql.FlatForward(eval_date, domestic_rate, day_count))
foreign_curve = ql.YieldTermStructureHandle(ql.FlatForward(eval_date, foreign_rate, day_count))

vol_handle = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(eval_date, calendar, volatility, day_count))

# Payoff and exercise
payoff = ql.PlainVanillaPayoff(option_type, strike_price)


# Define the process for the underlying
#fx_process = ql.BlackScholesProcess(spot_handle, foreign_curve, vol_handle)

# Pricing engine
#engine = ql.BaroneAdesiWhaleyApproximationEngine(fx_process)
fx_process = ql.BlackScholesMertonProcess(
    spot_handle, foreign_curve, domestic_curve, vol_handle
)
engine = ql.BaroneAdesiWhaleyApproximationEngine(fx_process)

# Construct FX option
fx_option = ql.VanillaOption(payoff, exercise)
fx_option.setPricingEngine(engine)



'''
delta = fx_option.delta()
gamma = fx_option.gamma()
vega = fx_option.vega()
theta = fx_option.theta()
rho = fx_option.rho()

delta_usd = delta / spot_price
gamma_usd = gamma / (spot_price ** 2)
vega_usd = vega / spot_price
theta_usd = theta / spot_price
rho_usd = rho / spot_price

print(f"  Delta (CNY): {delta*notional:.6f}")
print(f"  Gamma (CNY): {gamma*notional:.6f}")
print(f"  Vega (CNY): {vega*notional:.6f}")
print(f"  Theta (CNY): {theta*notional:.6f}")
print(f"  Rho (CNY): {rho*notional:.6f}")

print(f"  Delta (USD): {delta_usd*notional:.6f}")
print(f"  Gamma (USD): {gamma_usd*notional:.6f}")
print(f"  Vega (USD): {vega_usd*notional:.6f}")
print(f"  Theta (USD): {theta_usd*notional:.6f}")
print(f"  Rho (USD): {rho_usd*notional:.6f}")


'''
# Convert Greeks to USD terms

# Calculate the option price and Greeks
npv = fx_option.NPV()
npv_usd = npv / spot_price

notional = 1_000_000

# Display results in CNY terms
print(f"Option evaluationDate: {ql.Settings.instance().evaluationDate}")
print(f"Option maturity_date: {maturity_date}")

print(f"Option Price (CNY): {npv*notional:.6f}")
print("Greeks (in CNY):")

# Display results in USD terms
print(f"Option Price (USD): {npv_usd*notional:.6f}")


def calculate_american_option_greeks(S, K, T, r, q, sigma, option_type=ql.Option.Call):
    # Market data
    spot_handle = ql.QuoteHandle(ql.SimpleQuote(S))
    volatility_handle = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(ql.Settings.instance().evaluationDate , ql.NullCalendar(), sigma, ql.Actual365Fixed())
    )
    risk_free_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(ql.Settings.instance().evaluationDate , ql.QuoteHandle(ql.SimpleQuote(r)), ql.Actual365Fixed())
    )
    dividend_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(ql.Settings.instance().evaluationDate , ql.QuoteHandle(ql.SimpleQuote(q)), ql.Actual365Fixed())
    )

    # Option definition
    payoff = ql.PlainVanillaPayoff(option_type, K)
    exercise = ql.AmericanExercise(ql.Settings.instance().evaluationDate , ql.Settings.instance().evaluationDate  + ql.Period(int(T * 365), ql.Days))
    option = ql.VanillaOption(payoff, exercise)

    # Black-Scholes-Merton Process
    bsm_process = ql.BlackScholesMertonProcess(spot_handle, dividend_handle, risk_free_handle, volatility_handle)

    # Pricing engine
    steps = 1000  # Number of binomial steps
    engine = ql.BinomialVanillaEngine(bsm_process, "crr", steps)
    option.setPricingEngine(engine)

    # Greeks
    npv = option.NPV()
    delta = option.delta()
    gamma = option.gamma()
    theta = option.theta()

    # Manual Vega Calculation using finite difference
    epsilon = 0.01  # Small perturbation in volatility
    vol_up_handle = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(ql.Settings.instance().evaluationDate , ql.NullCalendar(), sigma + epsilon, ql.Actual365Fixed())
    )
    vol_down_handle = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(ql.Settings.instance().evaluationDate , ql.NullCalendar(), sigma - epsilon, ql.Actual365Fixed())
    )
    bsm_process_up = ql.BlackScholesMertonProcess(spot_handle, dividend_handle, risk_free_handle, vol_up_handle)
    bsm_process_down = ql.BlackScholesMertonProcess(spot_handle, dividend_handle, risk_free_handle, vol_down_handle)

    option.setPricingEngine(ql.BinomialVanillaEngine(bsm_process_up, "crr", steps))
    npv_up = option.NPV()

    option.setPricingEngine(ql.BinomialVanillaEngine(bsm_process_down, "crr", steps))
    npv_down = option.NPV()

    vega = (npv_up - npv_down) / (2 * epsilon)

    # Manual Rho Calculation using finite difference
    epsilon_r = 0.0001  # Small perturbation in interest rate
    rate_up_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(ql.Settings.instance().evaluationDate , ql.QuoteHandle(ql.SimpleQuote(r + epsilon_r)), ql.Actual365Fixed())
    )
    rate_down_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(ql.Settings.instance().evaluationDate , ql.QuoteHandle(ql.SimpleQuote(r - epsilon_r)), ql.Actual365Fixed())
    )
    bsm_process_up = ql.BlackScholesMertonProcess(spot_handle, dividend_handle, rate_up_handle, volatility_handle)
    bsm_process_down = ql.BlackScholesMertonProcess(spot_handle, dividend_handle, rate_down_handle, volatility_handle)

    option.setPricingEngine(ql.BinomialVanillaEngine(bsm_process_up, "crr", steps))
    npv_up = option.NPV()

    option.setPricingEngine(ql.BinomialVanillaEngine(bsm_process_down, "crr", steps))
    npv_down = option.NPV()

    rho = (npv_up - npv_down) / (2 * epsilon_r)

    return npv, delta, gamma, theta, vega, rho

price, delta, gamma, theta, vega, rho = \
    calculate_american_option_greeks(spot_price, strike_price, maturity_in_years, domestic_rate, foreign_rate, volatility)

print("Greeks BinomialVanillaEngine")
print(f"Price: {price*notional}")
print(f"Delta: {delta*notional}")
print(f"Gamma: {gamma}")
print(f"Theta: {theta}")
print(f"Vega: {vega}")
print(f"Rho: {rho}")
