import QuantLib as ql
from datetime import datetime
import math

#NOT working
def calculate_strike_and_vol(spot, forward_rate, forward_delta, maturity_date, risk_free_rate_base,
                             risk_free_rate_quote, initial_vol_guess=0.1, is_call=True):
    """
    Calculate strike and implied volatility for FX option using forward delta as input

    Parameters:
    spot (float): Current spot rate
    forward_rate (float): Forward rate
    forward_delta (float): Forward delta (absolute value between 0 and 1)
    maturity_date (datetime): Option expiry date
    risk_free_rate_base (float): Risk-free rate for base currency (USD)
    risk_free_rate_quote (float): Risk-free rate for quote currency (CNY)
    initial_vol_guess (float): Initial guess for implied volatility
    is_call (bool): True for call option, False for put option

    Returns:
    tuple: (strike, implied_volatility)
    """
    # Input validation
    if not (0 < forward_delta < 1):
        raise ValueError(f"Forward delta must be between 0 and 1, got {forward_delta}")
    if spot <= 0 or forward_rate <= 0:
        raise ValueError("Spot and forward rates must be positive")
    if initial_vol_guess <= 0:
        raise ValueError("Initial volatility guess must be positive")

    # Convert dates to QuantLib format
    calculation_date = ql.Date().todaysDate()
    ql.Settings.instance().evaluationDate = calculation_date

    maturity_ql = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)

    # Verify maturity is in the future
    if maturity_ql <= calculation_date:
        raise ValueError("Maturity date must be in the future")

    # Set up the option parameters
    day_count = ql.Actual365Fixed()
    calendar = ql.China()

    # Calculate time to maturity
    t = day_count.yearFraction(calculation_date, maturity_ql)
    if t <= 0:
        raise ValueError("Time to maturity must be positive")

    # Set up the FX rate process
    spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot))
    rTS_base = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, risk_free_rate_base, day_count))
    rTS_quote = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, risk_free_rate_quote, day_count))

    # Initialize volatility
    vol = initial_vol_guess
    tolerance = 1.0e-5
    max_iterations = 100

    # Newton-Raphson iteration to find implied volatility that gives desired forward delta
    for i in range(max_iterations):
        try:
            vol_handle_simple_q = ql.QuoteHandle(ql.SimpleQuote(vol))

            # Create the Black-Scholes process
            #bsm_process = ql.GarmanKohlhagenProcess(spot_handle, rTS_base, rTS_quote, vol_handle)

            vol_handle = ql.BlackVolTermStructureHandle(
                ql.BlackConstantVol(0, ql.UnitedStates(ql.UnitedStates.Settlement), vol_handle_simple_q,
                                    ql.ActualActual(ql.ActualActual.Actual365)))
            # Create the Black-Scholes process
            bsm_process = ql.GarmanKohlagenProcess(spot_handle, rTS_base, rTS_quote, vol_handle)

            # Calculate strike using the Garman-Kohlhagen formula
            d1 = (math.log(forward_rate / forward_rate) + (vol * vol / 2) * t) / (vol * math.sqrt(t))
            if is_call:
                target_d1 = ql.InverseCumulativeNormal()(forward_delta)
            else:
                target_d1 = ql.InverseCumulativeNormal()(forward_delta - 1)

            strike = forward_rate * math.exp(-target_d1 * vol * math.sqrt(t) + 0.5 * vol * vol * t)

            # Create the option with calculated strike
            payoff = ql.PlainVanillaPayoff(ql.Option.Call if is_call else ql.Option.Put, strike)
            exercise = ql.EuropeanExercise(maturity_ql)
            option = ql.VanillaOption(payoff, exercise)

            # Set up the pricing engine
            engine = ql.AnalyticEuropeanEngine(bsm_process)
            option.setPricingEngine(engine)

            calculated_delta = option.delta()

            # Check if we've reached desired accuracy
            if abs(calculated_delta - (forward_delta if is_call else -forward_delta)) < tolerance:
                return strike, vol

            # Update volatility guess with dampening factor to prevent overshooting
            dampening = 0.5
            vol = vol * (1.0 + dampening * (calculated_delta - (forward_delta if is_call else -forward_delta)))

            # Add bounds for volatility to prevent extreme values
            vol = max(0.0001, min(vol, 2.0))

        except Exception as e:
            print(f"Iteration {i} failed with error: {str(e)}")
            print(f"Current vol: {vol}, Current strike: {strike}")
            raise

    raise RuntimeError("Failed to converge after maximum iterations")


# Example usage
if __name__ == "__main__":
    try:
        # Example market data
        spot = 7.1500  # USD/CNY spot rate
        forward_rate = 7.2000  # USD/CNY forward rate
        forward_delta = 0.25  # 25 delta
        maturity_date = datetime(2027, 6, 15)
        risk_free_rate_usd = 0.05  # 5% USD rate
        risk_free_rate_cny = 0.03  # 3% CNY rate

        strike, implied_vol = calculate_strike_and_vol(
            spot=spot,
            forward_rate=forward_rate,
            forward_delta=forward_delta,
            maturity_date=maturity_date,
            risk_free_rate_base=risk_free_rate_usd,
            risk_free_rate_quote=risk_free_rate_cny,
            is_call=True
        )

        print(f"Calculated Strike: {strike:.4f}")
        print(f"Implied Volatility: {implied_vol:.4f}")

    except Exception as e:
        print(f"Calculation failed: {str(e)}")