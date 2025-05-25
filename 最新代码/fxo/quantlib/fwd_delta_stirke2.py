import QuantLib as ql
import math

# Set the evaluation date
evaluation_date = ql.Date(31, 10, 2023)
ql.Settings.instance().evaluationDate = evaluation_date

# Define market data and option parameters
spot_price = 7.12  # USD/CNY spot price
domestic_rate = 4.3465/100 # USD interest rate (domestic)
foreign_rate = 2.122/100 # CNY interest rate (foreign)
maturity_date = ql.Date(4, 11, 2027)
#time_to_maturity = 3.0  # Time to maturity in years
day_count = ql.Actual365Fixed()
time_to_maturity = day_count.yearFraction(evaluation_date, maturity_date)
forward_delta = 0.15  # Given forward delta
volatility = 6.0722/100  # Assumed volatility for strike calculation

# Calculate forward price
forward_price = spot_price * math.exp((domestic_rate - foreign_rate) * time_to_maturity)
print(f"Forward Price: {forward_price:.4f}")

# Step 1: Calculate Strike Price given Forward Delta and Volatility
# Use inverse cumulative normal distribution to get d1
#d1_inverse = ql.NormalDistribution().inverseCumulative(forward_delta)
d1_inverse = ql.InverseCumulativeNormal()
d1_inverse_val = d1_inverse(forward_delta)
strike_price = forward_price * math.exp(
    -volatility * math.sqrt(time_to_maturity) * d1_inverse_val +
    (volatility * volatility / 2) * time_to_maturity
)
print(f"Calculated Strike Price: {strike_price:.4f}")

# Step 2: Calculate Implied Volatility given Forward Delta and Strike
# Define the error function for volatility solving
def error_function(sigma, forward_price, strike, time_to_maturity, forward_delta):
    if sigma <= 0:
        return 1.0  # Avoid division by zero
    d1 = (math.log(forward_price / strike) + (sigma * sigma / 2) * time_to_maturity) / \
         (sigma * math.sqrt(time_to_maturity))
    calculated_delta = ql.NormalDistribution()(d1)
    return forward_delta - calculated_delta

# Use Brent solver to find volatility
solver = ql.Brent()
accuracy = 1e-8
guess = 0.20  # Initial guess for volatility
lower_bound = 0.01
upper_bound = 1.0

implied_volatility = solver.solve(
    lambda sigma: error_function(sigma, forward_price, strike_price, time_to_maturity, forward_delta),
    accuracy, guess, lower_bound, upper_bound
)
print(f"Implied Volatility: {implied_volatility:.4f}")

# Optional: Verify with Black-Scholes model (for completeness)
calendar = ql.NullCalendar()
day_count = ql.Actual365Fixed()

# Set up dates
#maturity_date = evaluation_date + int(time_to_maturity * 365)


# Define yield curves and volatility
domestic_ts = ql.FlatForward(evaluation_date, domestic_rate, day_count)
foreign_ts = ql.FlatForward(evaluation_date, foreign_rate, day_count)
vol_ts = ql.BlackConstantVol(evaluation_date, calendar, implied_volatility, day_count)

# Spot handle and process
spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
process = ql.BlackScholesMertonProcess(
    spot_handle,
    ql.YieldTermStructureHandle(foreign_ts),  # Dividend yield = foreign rate
    ql.YieldTermStructureHandle(domestic_ts),  # Risk-free rate = domestic rate
    ql.BlackVolTermStructureHandle(vol_ts)
)

# Define option
option_type = ql.Option.Call  # or ql.Option.Put
exercise = ql.EuropeanExercise(maturity_date)
payoff = ql.PlainVanillaPayoff(option_type, strike_price)
option = ql.VanillaOption(payoff, exercise)

# Price the option
#engine = ql.BlackScholesCalculator(process)
engine = ql.AnalyticEuropeanEngine(process)
option.setPricingEngine(engine)
option_price = option.NPV()
delta = option.delta()

print(f"Option Price: {option_price:.4f}")
print(f"Calculated Forward Delta (verification): {delta * math.exp(-foreign_rate * time_to_maturity):.4f}")