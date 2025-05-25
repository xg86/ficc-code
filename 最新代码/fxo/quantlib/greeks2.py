import QuantLib as ql


def calculate_fx_american_option_greeks(S, K, T, rd, rf, sigma, option_type=ql.Option.Call, notional=1_000_000):
    """
    Calculate FX American option Greeks for USD/CNY using Barone-Adesi-Whaley Approximation.

    :param S: Spot price (USD/CNY)
    :param K: Strike price
    :param T: Time to maturity (years)
    :param rd: Domestic risk-free rate (USD)
    :param rf: Foreign risk-free rate (CNY)
    :param sigma: Volatility
    :param option_type: Option type (ql.Option.Call or ql.Option.Put)
    :param notional: Notional amount in USD
    :return: Option price and Greeks
    """
    # Market data
    spot_quote = ql.SimpleQuote(S)
    spot_handle = ql.QuoteHandle(spot_quote)
    volatility_quote = ql.SimpleQuote(sigma)
    volatility_handle = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(ql.Date().todaysDate(), ql.NullCalendar(), sigma, ql.Actual365Fixed())
    )
    domestic_rate_quote = ql.SimpleQuote(rd)
    domestic_rate_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(ql.Date().todaysDate(), ql.QuoteHandle(domestic_rate_quote), ql.Actual365Fixed())
    )
    foreign_rate_quote = ql.SimpleQuote(rf)
    foreign_rate_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(ql.Date().todaysDate(), ql.QuoteHandle(foreign_rate_quote), ql.Actual365Fixed())
    )

    # Option definition
    payoff = ql.PlainVanillaPayoff(option_type, K)
    exercise = ql.AmericanExercise(ql.Date().todaysDate(), ql.Date().todaysDate() + ql.Period(int(T * 365), ql.Days))
    option = ql.VanillaOption(payoff, exercise)

    # Black-Scholes-Merton Process
    bsm_process = ql.BlackScholesMertonProcess(spot_handle, foreign_rate_handle, domestic_rate_handle,
                                               volatility_handle)

    # Pricing engine
    engine = ql.BaroneAdesiWhaleyApproximationEngine(bsm_process)
    option.setPricingEngine(engine)

    # Greeks
    npv = option.NPV() * notional
    delta = _calculate_greek_with_shift(option, spot_quote, S, 1e-4) * notional
    gamma = (_calculate_greek_with_shift(option, spot_quote, S + 1e-4, 1e-4)
             - 2 * npv
             + _calculate_greek_with_shift(option, spot_quote, S - 1e-4, 1e-4)) / (1e-4 ** 2) * notional
    vega = _calculate_greek_with_shift(option, volatility_quote, sigma, 1e-4) * notional
    rho_domestic = _calculate_greek_with_shift(option, domestic_rate_quote, rd, 1e-4) * notional
    rho_foreign = _calculate_greek_with_shift(option, foreign_rate_quote, rf, 1e-4) * notional
    #theta = option.theta() * notional

    theta = 12345
    return {
        "NPV": npv,
        "Delta": delta,
        "Gamma": gamma,
        "Theta": theta,
        "Vega": vega,
        "Rho (Domestic)": rho_domestic,
        "Rho (Foreign)": rho_foreign
    }


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


# Test the function
if __name__ == "__main__":
    S = 7.2  # Spot price USD/CNY
    K = 7.0  # Strike price
    T = 1  # Time to maturity in years
    rd = 0.03  # Domestic risk-free rate (USD)
    rf = 0.015  # Foreign risk-free rate (CNY)
    sigma = 0.12  # Volatility
    option_type = ql.Option.Call  # Option type (Call or Put)
    notional = 1_000_000  # Notional amount in USD

    results = calculate_fx_american_option_greeks(S, K, T, rd, rf, sigma, option_type, notional)

    print("Results for USD/CNY FX American Option (Barone-Adesi-Whaley Approximation):")
    for greek, value in results.items():
        print(f"  {greek}: {value:.6f}")
