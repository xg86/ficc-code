import QuantLib as ql
calculation_date = ql.Date(31, 10, 2024)  # Calculation date (15th October 2023)
spot_price = 7.12  # Current spot price of USD/CNY
# Define the parameters for the FX option


strike_price = 6.8303# Strike price of the option
volatility = 6.137/100  # 10% volatility
domestic_rate = 2.1225/100 # CNY risk-free rate (domestic currency)
foreign_rate = 4.3465/100   # USD risk-free rate (foreign currency)
maturity_date = ql.Date(4, 11, 2027)
option_type = ql.Option.Call  # Change to ql.Option.Call for a Call option
ql.ModifiedFollowing
#6D
'''
strike_price = 7.07  # Strike price of the option
volatility = 8.12178056178724/100  # 10% volatility
domestic_rate = 1.55614086534798/100 # CNY risk-free rate (domestic currency)
foreign_rate = 4.12568224828235/100   # USD risk-free rate (foreign currency)
maturity_date = ql.Date(6, 11, 2024)
option_type = ql.Option.Put  # Change to ql.Option.Call for a Call option

#The price of the American-style USD/CNY FX Put option is: 117.4185
#The price of the European -1 option for USD/CNY is: 117.3853

#5D

strike_price = 7.14  # Strike price of the option
volatility = 4.20902/100  # 10% volatility
domestic_rate = 1.52738/100 # CNY risk-free rate (domestic currency)
foreign_rate = 4.01554/100  # USD risk-free rate (foreign currency)
maturity_date = ql.Date(5, 11, 2024)
option_type = ql.Option.Call  # Change to ql.Option.Call for a Call option
#The price of the American-style USD/CNY FX Call option is: 56.1344
#The price of the European 1 option for USD/CNY is:  55.5928
'''

# Set the evaluation date
ql.Settings.instance().evaluationDate = calculation_date

# Define the currency pair
currency_pair = "USD/CNY"

# Create the quote for the spot price
spot_quote = ql.SimpleQuote(spot_price)

# Create the yield term structures for domestic and foreign rates
domestic_curve = ql.FlatForward(calculation_date, domestic_rate, ql.Actual365Fixed())
foreign_curve = ql.FlatForward(calculation_date, foreign_rate, ql.Actual365Fixed())

# Create the Black-Scholes process
spot_handle = ql.QuoteHandle(spot_quote)
domestic_handle = ql.YieldTermStructureHandle(domestic_curve)
foreign_handle = ql.YieldTermStructureHandle(foreign_curve)

volatility_quote = ql.SimpleQuote(volatility)
volatility_handle = ql.BlackVolTermStructureHandle(
    ql.BlackConstantVol(calculation_date, ql.NullCalendar(), ql.QuoteHandle(volatility_quote), ql.Actual365Fixed())
)

# Use the Black-Scholes-Merton process for FX options
bsm_process = ql.BlackScholesMertonProcess(spot_handle, foreign_handle, domestic_handle, volatility_handle)

# Create the European option
payoff = ql.PlainVanillaPayoff(option_type, strike_price)
exercise = ql.EuropeanExercise(maturity_date)
european_option = ql.VanillaOption(payoff, exercise)

# Set up the pricing engine
pricing_engine = ql.AnalyticEuropeanEngine(bsm_process)
european_option.setPricingEngine(pricing_engine)

# Calculate the option price
option_price = european_option.NPV()
print(f"The price of the European {option_type} option for {currency_pair} is: {option_price*1_000_000:.4f}")
print(f"The fwddelta of the European {option_type} option for {currency_pair} is: {european_option.deltaForward()*1_000_000:.4f}")
print(f"The delta of the European {option_type} option for {currency_pair} is: {european_option.delta()*1_000_000:.4f}")