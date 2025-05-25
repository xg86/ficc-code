import QuantLib as ql

# FX Option parameters
spot_price = 7.12  # Spot price (USD/CNY)
strike_price = 7.14  # Strike price (USD/CNY)
maturity_in_years = 1.0/365  # Time to maturity in years
domestic_rate = 0.0147  # Domestic risk-free rate (CNY, in decimal form)
foreign_rate = 0.04404  # Foreign risk-free rate (must be USD, in decimal form)
volatility = 4.336384/100  # Implied volatility (in decimal form)
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

spot_quote = ql.SimpleQuote(spot_price)
spot_handle = ql.QuoteHandle(spot_quote)

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

def _calculate_greek_with_shift(option, quote, original_value, epsilon):
    """Helper function to calculate Greeks using finite difference."""
    # Save the original value
    original = quote.value()

    # Shift the value up
    quote.setValue(original_value + epsilon)
    npv_up = option.NPV()

    # Shift the value down
    quote.setValue(original_value - epsilon)
    npv_down = option.NPV()

    # Reset the quote to the original value
    quote.setValue(original)

    return (npv_up - npv_down) / (2 * epsilon)

# Greeks
delta = _calculate_greek_with_shift(fx_option, spot_quote, spot_price, 1e-4)
'''
gamma = (_calculate_greek_with_shift(fx_option, spot_quote, spot_price + 1e-4, 1e-4)
         - 2 * npv
         + _calculate_greek_with_shift(fx_option, spot_quote, spot_price - 1e-4, 1e-4)) / (1e-4 ** 2)

volatility_quote = ql.SimpleQuote(volatility)
'''

# Manual Gamma Calculation using finite difference
epsilon = 0.0001
spot_price_up = spot_price + epsilon
spot_quote_up = ql.SimpleQuote(spot_price_up)
spot_handle_up = ql.QuoteHandle(spot_quote_up)
bsm_process_up = ql.BlackScholesMertonProcess(spot_handle_up, foreign_curve,   domestic_curve, vol_handle)
fx_option_up = ql.VanillaOption(payoff, exercise)
fx_option_up.setPricingEngine(ql.BaroneAdesiWhaleyApproximationEngine(bsm_process_up))
price_up = fx_option_up.NPV()
#delta_up =_calculate_greek_with_shift(fx_option, spot_quote_up, spot_price_up, epsilon)
#delta_up = fx_option.delta()

spot_price_down = spot_price - epsilon
spot_quote_down = ql.SimpleQuote(spot_price_down)
spot_handle_down = ql.QuoteHandle(spot_quote_down)
bsm_process_down = ql.BlackScholesMertonProcess(spot_handle_down, foreign_curve, domestic_curve, vol_handle)
fx_option_down= ql.VanillaOption(payoff, exercise)
fx_option_down.setPricingEngine(ql.BaroneAdesiWhaleyApproximationEngine(bsm_process_down))
price_down = fx_option_down.NPV()
#delta_down = _calculate_greek_with_shift(fx_option, spot_quote_down, spot_price_down, epsilon)

#gamma = (delta_up - delta_down) / (2 * epsilon)
#gamma = (delta_up - 2 * npv + delta_down) / (epsilon ** 2)
gamma = (price_up - 2 * npv + price_down) / (epsilon ** 2)

#vega = _calculate_greek_with_shift(fx_option, volatility_quote, volatility, 0.01)

# Manual Vega Calculation using finite difference
epsilon = 0.01  # Small perturbation in volatility
vol_up_handle = ql.BlackVolTermStructureHandle(
    ql.BlackConstantVol(ql.Settings.instance().evaluationDate, ql.NullCalendar(), volatility + epsilon, ql.Actual365Fixed())
)
vol_down_handle = ql.BlackVolTermStructureHandle(
    ql.BlackConstantVol(ql.Settings.instance().evaluationDate, ql.NullCalendar(), volatility - epsilon, ql.Actual365Fixed())
)
bsm_process_up = ql.BlackScholesMertonProcess(spot_handle, foreign_curve, domestic_curve, vol_up_handle)
bsm_process_down = ql.BlackScholesMertonProcess(spot_handle, foreign_curve, domestic_curve, vol_down_handle)

fx_option.setPricingEngine(ql.BaroneAdesiWhaleyApproximationEngine(bsm_process_up))
npv_up = fx_option.NPV()

fx_option.setPricingEngine(ql.BaroneAdesiWhaleyApproximationEngine(bsm_process_down))
npv_down = fx_option.NPV()

vega = (npv_up - npv_down) / (2 * epsilon)
################################################################
foreign_rate_quote = ql.SimpleQuote(foreign_rate)
domestic_rate_quote = ql.SimpleQuote(domestic_rate)
#rho_domestic = _calculate_greek_with_shift(fx_option, foreign_rate_quote, foreign_rate , 1e-4)
#rho_foreign = _calculate_greek_with_shift(fx_option, domestic_rate_quote, domestic_rate, 1e-4)

# Manual Rho Calculation using finite difference
epsilon_r = 0.0001  # Small perturbation in interest rate
rate_up_handle = ql.YieldTermStructureHandle(
    ql.FlatForward(ql.Settings.instance().evaluationDate, ql.QuoteHandle(ql.SimpleQuote(domestic_rate + epsilon_r)),
                   ql.Actual365Fixed())
)
rate_down_handle = ql.YieldTermStructureHandle(
    ql.FlatForward(ql.Settings.instance().evaluationDate, ql.QuoteHandle(ql.SimpleQuote(domestic_rate - epsilon_r)),
                   ql.Actual365Fixed())
)
bsm_process_up = ql.BlackScholesMertonProcess(spot_handle, foreign_curve, rate_up_handle, vol_handle)
bsm_process_down = ql.BlackScholesMertonProcess(spot_handle, foreign_curve, rate_down_handle, vol_handle)

fx_option.setPricingEngine(ql.BaroneAdesiWhaleyApproximationEngine(bsm_process_up))
npv_up = fx_option.NPV()

fx_option.setPricingEngine(ql.BaroneAdesiWhaleyApproximationEngine(bsm_process_down))
npv_down = fx_option.NPV()

rho = (npv_up - npv_down) / (2 * epsilon_r)

results =  {
    "NPV": npv,
    "Delta": delta*notional,
    "Gamma BaroneAdesiWhaleyApproximationEngine wrong": gamma*10_000,
    "Theta": 19741212,
    "Vega(CNY)": vega*10_000,
    "Rho (CNY)": rho*10_000
  #  "Rho (Foreign)": rho_foreign
}

for greek, value in results.items():
    print(f"  {greek}: {value:.6f}")