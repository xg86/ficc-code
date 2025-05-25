import QuantLib as ql

# Define the option parameters
'''
spot_price = 6.50  # Current USD/CNY spot exchange rate
strike_price = 6.60  # Strike price of the option
volatility = 0.10  # 10% volatility
domestic_rate = 0.03  # CNY risk-free rate (domestic currency)
foreign_rate = 0.01  # USD risk-free rate (foreign currency)
maturity_date = ql.Date(15, 7, 2024)
option_type = ql.Option.Put  # Change to ql.Option.Call for a Call option
'''
spot_price = 7.12 # Current USD/CNY spot exchange rate
evaluation_date = ql.Date(31, 10, 2024)
#1Y
'''
strike_price = 7.75  # Strike price of the option
volatility = 6.95692/100   # 10% volatility
domestic_rate = 1.92927/100 # CNY risk-free rate (domestic currency)
foreign_rate = 4.96882/100  # USD risk-free rate (foreign currency)
maturity_date = ql.Date(4, 11, 2025)
option_type = ql.Option.Call  # Change to ql.Option.Call for a Call option
# The price of the American-style USD/CNY FX Call option is: 114.2633
'''
#5D
'''
strike_price = 7.14  # Strike price of the option
volatility = 4.20902/100  # 10% volatility
domestic_rate = 1.52738/100 # CNY risk-free rate (domestic currency)
foreign_rate = 4.01554/100  # USD risk-free rate (foreign currency)
maturity_date = ql.Date(5, 11, 2024)
option_type = ql.Option.Call  # Change to ql.Option.Call for a Call option
#The price of the American-style USD/CNY FX Call option is: 56.1344


#6D
strike_price = 7.07  # Strike price of the option
volatility = 8.12178056178724/100  # 10% volatility
domestic_rate = 1.55614086534798/100 # CNY risk-free rate (domestic currency)
foreign_rate = 4.12568224828235/100   # USD risk-free rate (foreign currency)
maturity_date = ql.Date(6, 11, 2024)
option_type = ql.Option.Put  # Change to ql.Option.Call for a Call option
'''
#6D
strike_price = 7.14  # Strike price of the option
volatility = 4.324/100  # 10% volatility
domestic_rate = 1.47/100 # CNY risk-free rate (domestic currency)
foreign_rate = 4.383/100   # USD risk-free rate (foreign currency)
maturity_date = ql.Date(1, 11, 2024)
option_type = ql.Option.Call  # Change to ql.Option.Call for a Call option
#The price of the American-style USD/CNY FX Put option is: 117.4185

ql.Settings.instance().evaluationDate = evaluation_date

# Create the option payoff and exercise
payoff = ql.PlainVanillaPayoff(option_type, strike_price)
exercise = ql.AmericanExercise(evaluation_date, maturity_date)

# Create the option object
option = ql.VanillaOption(payoff, exercise)


# Create the spot curve (USD/CNY spot rate)
spot_curve = ql.FlatForward(evaluation_date, ql.QuoteHandle(ql.SimpleQuote(spot_price)), ql.Actual365Fixed())

# Create the domestic (CNY) risk-free rate curve
domestic_curve = ql.FlatForward(evaluation_date, domestic_rate, ql.Actual365Fixed())

# Create the foreign (USD) risk-free rate curve
foreign_curve = ql.FlatForward(evaluation_date, foreign_rate, ql.Actual365Fixed())

# Create the Black-Scholes process for FX options
fx_process = ql.BlackScholesMertonProcess(
    ql.QuoteHandle(ql.SimpleQuote(spot_price)),
    ql.YieldTermStructureHandle(foreign_curve),  # Foreign rate (USD)
    ql.YieldTermStructureHandle(domestic_curve),  # Domestic rate (CNY)
    ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evaluation_date, ql.NullCalendar(), volatility, ql.Actual365Fixed()))
)

# Create the PDE solver (using Finite Differences)
time_steps = 100
grid_points = 100
solver = ql.FdBlackScholesVanillaEngine(fx_process, time_steps, grid_points)

# Set the pricing engine for the option
option.setPricingEngine(solver)

# Calculate the option price
option_price = option.NPV()
option_type_str = "Call" if option_type == ql.Option.Call else "Put"
print(f"The price of the American-style USD/CNY FX {option_type_str} option is: {option_price*10000:.4f}")
print("Delta is:", option.delta()/24*21)
print("gamma is:", option.gamma()/24*21)

#print("deltaForward is:", option.deltaForward()*1_000_000)