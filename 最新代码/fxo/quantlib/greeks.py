import QuantLib as ql


def calculate_american_fx_option_greeks(S, K, T, r, q, sigma, option_type=ql.Option.Call):
    # Setup market data
    spot_handle = ql.QuoteHandle(ql.SimpleQuote(S))
    volatility_handle = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(ql.Date().todaysDate(), ql.NullCalendar(), sigma, ql.Actual365Fixed())
    )
    risk_free_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(ql.Date().todaysDate(), ql.QuoteHandle(ql.SimpleQuote(r)), ql.Actual365Fixed())
    )
    dividend_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(ql.Date().todaysDate(), ql.QuoteHandle(ql.SimpleQuote(q)), ql.Actual365Fixed())
    )

    # Define the American-style option
    payoff = ql.PlainVanillaPayoff(option_type, K)
    exercise = ql.AmericanExercise(ql.Date().todaysDate(), ql.Date().todaysDate() + ql.Period(int(T * 365), ql.Days))
    option = ql.VanillaOption(payoff, exercise)

    # Black-Scholes-Merton process
    bsm_process = ql.BlackScholesMertonProcess(spot_handle, dividend_handle, risk_free_handle, volatility_handle)

    # Pricing engine using Binomial method
    steps = 1000
    engine = ql.BinomialVanillaEngine(bsm_process, "crr", steps)
    option.setPricingEngine(engine)

    # Calculate option price and Greeks
    price = option.NPV()
    delta = option.delta()
    theta = option.theta()

    # Manual Gamma Calculation using finite difference
    epsilon = 0.01
    spot_handle_up = ql.QuoteHandle(ql.SimpleQuote(S + epsilon))
    spot_handle_down = ql.QuoteHandle(ql.SimpleQuote(S - epsilon))
    bsm_process_up = ql.BlackScholesMertonProcess(spot_handle_up, dividend_handle, risk_free_handle, volatility_handle)
    bsm_process_down = ql.BlackScholesMertonProcess(spot_handle_down, dividend_handle, risk_free_handle,
                                                    volatility_handle)

    option.setPricingEngine(ql.BinomialVanillaEngine(bsm_process_up, "crr", steps))
    price_up = option.NPV()
    delta_up = option.delta()

    option.setPricingEngine(ql.BinomialVanillaEngine(bsm_process_down, "crr", steps))
    price_down = option.NPV()
    delta_down = option.delta()

    gamma = (delta_up - delta_down) / (2 * epsilon)

    # Manual Vega Calculation using finite difference
    vol_up_handle = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(ql.Date().todaysDate(), ql.NullCalendar(), sigma + epsilon, ql.Actual365Fixed())
    )
    vol_down_handle = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(ql.Date().todaysDate(), ql.NullCalendar(), sigma - epsilon, ql.Actual365Fixed())
    )
    bsm_process_vol_up = ql.BlackScholesMertonProcess(spot_handle, dividend_handle, risk_free_handle, vol_up_handle)
    bsm_process_vol_down = ql.BlackScholesMertonProcess(spot_handle, dividend_handle, risk_free_handle, vol_down_handle)

    option.setPricingEngine(ql.BinomialVanillaEngine(bsm_process_vol_up, "crr", steps))
    price_vol_up = option.NPV()

    option.setPricingEngine(ql.BinomialVanillaEngine(bsm_process_vol_down, "crr", steps))
    price_vol_down = option.NPV()

    vega = (price_vol_up - price_vol_down) / (2 * epsilon)

    # Manual Rho Calculation using finite difference
    epsilon_r = 0.0001
    r_up_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(ql.Date().todaysDate(), ql.QuoteHandle(ql.SimpleQuote(r + epsilon_r)), ql.Actual365Fixed()))
    r_down_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(ql.Date().todaysDate(), ql.QuoteHandle(ql.SimpleQuote(r - epsilon_r)), ql.Actual365Fixed()))
    bsm_process_r_up = ql.BlackScholesMertonProcess(spot_handle, dividend_handle, r_up_handle, volatility_handle)
    bsm_process_r_down = ql.BlackScholesMertonProcess(spot_handle, dividend_handle, r_down_handle, volatility_handle)

    option.setPricingEngine(ql.BinomialVanillaEngine(bsm_process_r_up, "crr", steps))
    price_r_up = option.NPV()

    option.setPricingEngine(ql.BinomialVanillaEngine(bsm_process_r_down, "crr", steps))
    price_r_down = option.NPV()

    rho = (price_r_up - price_r_down) / (2 * epsilon_r)

    return price, delta, gamma, theta, vega, rho


# Example usage
'''
S = 147.8  # Spot price
K = 145  # Strike price
T = 1  # Time to maturity in years
r = 0.02  # Risk-free interest rate
q = 0.01  # Foreign risk-free rate
sigma = 0.15  # Volatility
'''

S = 7.12  # Spot price (USD/CNY)
K = 7.75  # Strike price (USD/CNY)
T = 1.0  # Time to maturity in years
r = 0.01929  # Domestic risk-free rate (CNY, in decimal form)
q  = 0.05032  # Foreign risk-free rate (must be USD, in decimal form)
sigma = 6.875/100  # Implied volatility (in decimal form)
price, delta, gamma, theta, vega, rho = calculate_american_fx_option_greeks(S, K, T, r, q, sigma)

print(f"Price: {price}")
print(f"Delta: {delta}")
print(f"Gamma: {gamma}")
print(f"Theta: {theta}")
print(f"Vega: {vega}")
print(f"Rho: {rho}")
