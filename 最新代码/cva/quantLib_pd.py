import QuantLib as ql
import numpy as np
import pandas as pd
from datetime import datetime


def calculate_survival_probability(
        valuation_date,
        credit_spread_curve,
        recovery_rate,
        tenor_years,
        day_count=ql.Actual365Fixed()
):
    """
    Calculate survival probability and PD using QuantLib

    Parameters:
    valuation_date: QuantLib.Date
    credit_spread_curve: List of (tenor, spread) tuples
    recovery_rate: float
    tenor_years: int
    day_count: QuantLib DayCounter
    """

    # Set evaluation date
    ql.Settings.instance().evaluationDate = valuation_date

    # Create schedule for the analysis
    end_date = valuation_date + ql.Period(tenor_years, ql.Years)
    schedule = ql.Schedule(
        valuation_date,
        end_date,
        ql.Period(6, ql.Months),
        ql.TARGET(),
        ql.Following,
        ql.Following,
        ql.DateGeneration.Forward,
        False
    )

    # Create risk-free rate curve (flat rate for simplicity)
    risk_free_rate = 0.02  # 2% flat rate
    day_counter = ql.Actual365Fixed()
    calendar = ql.TARGET()

    rf_curve = ql.FlatForward(
        2,
        calendar,
        ql.QuoteHandle(ql.SimpleQuote(risk_free_rate)),
        day_counter
    )

    rf_curve_handle = ql.YieldTermStructureHandle(rf_curve)

    # Create credit default swap helpers
    helpers = []
    for tenor, spread in credit_spread_curve:
        tenor_period = ql.Period(tenor, ql.Years)
        spread_quote = ql.QuoteHandle(ql.SimpleQuote(spread / 10000.0))

        helper = ql.SpreadCdsHelper(
            spread_quote,
            tenor_period,
            0,
            calendar,
            ql.Quarterly,
            ql.Following,
            ql.DateGeneration.Forward,
            day_counter,
            recovery_rate,
            rf_curve_handle
        )
        helpers.append(helper)

    # Create hazard rate curve using bootstrapping
    probability_curve = ql.PiecewiseFlatHazardRate(
        0,
        calendar,
        helpers,
        day_counter
    )

    # Enable extrapolation
    probability_curve.enableExtrapolation()

    # Calculate survival probabilities and PDs
    results = []
    prev_survival_prob = 1.0

    for date in schedule:
        t = day_counter.yearFraction(valuation_date, date)
        survival_prob = probability_curve.survivalProbability(t)
        pdefault = 1.0 - survival_prob
        marginal_pd = prev_survival_prob - survival_prob

        results.append({
            'Date': date.to_date(),
            'Time': t,
            'Survival_Probability': survival_prob,
            'Cumulative_PD': pdefault,
            'Marginal_PD': marginal_pd,
            'Hazard_Rate': probability_curve.hazardRate(t)
        })

        prev_survival_prob = survival_prob
    return pd.DataFrame(results)


def main():
    # Example usage
    valuation_date = ql.Date(30, 1, 2025)

    # Sample credit spread curve (tenor in years, spread in bps)
    credit_spread_curve = [
        (1, 100),  # 1Y spread = 100 bps
        (2, 120),  # 2Y spread = 120 bps
        (3, 150),  # 3Y spread = 150 bps
        (5, 200),  # 5Y spread = 200 bps
        (7, 220),  # 7Y spread = 220 bps
        (10, 250)  # 10Y spread = 250 bps
    ]

    recovery_rate = 0.4  # 40% recovery rate
    tenor_years = 10

    try:
        results = calculate_survival_probability(
            valuation_date,
            credit_spread_curve,
            recovery_rate,
            tenor_years
        )

        # Print results
        pd.set_option('display.float_format', lambda x: '%.4f' % x)
        print("\nSurvival Probability and PD Analysis:")
        print(results)

        # Calculate some risk metrics
        print("\nRisk Metrics:")
        print(f"1-year PD: {results[results['Time'] <= 1.0]['Marginal_PD'].sum():.4%}")
        print(f"5-year cumulative PD: {results[results['Time'] <= 5.0]['Marginal_PD'].sum():.4%}")
        print(f"10-year cumulative PD: {results['Marginal_PD'].sum():.4%}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()