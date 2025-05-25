import math
import numpy as np
from scipy.stats import norm


def calculate_fx_option_gamma(
        spot_rate: float,
        strike_price: float,
        domestic_rate: float,
        foreign_rate: float,
        volatility: float,
        time_to_maturity: float
) -> float:
    """
    Calculate Gamma for an FX Option

    Parameters:
    - spot_rate: Current spot exchange rate
    - strike_price: Strike price of the option
    - domestic_rate: Domestic interest rate
    - foreign_rate: Foreign interest rate
    - volatility: Volatility of the exchange rate
    - time_to_maturity: Time to option maturity (in years)

    Returns:
    - Gamma value of the FX option
    """
    # Calculate d1
    d1 = (
                 math.log(spot_rate / strike_price) +
                 (domestic_rate - foreign_rate + 0.5 * volatility ** 2) * time_to_maturity
         ) / (volatility * math.sqrt(time_to_maturity))

    # Calculate Gamma
    gamma = norm.pdf(d1) / (spot_rate * volatility * math.sqrt(time_to_maturity))

    d1 = (math.log(S / K) + (r_d - r_f + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    gamma_value = norm.pdf(d1) / (S * sigma * math.sqrt(T))
    return gamma_value
    return gamma


# Example usage
def main():
    # Example parameters
    '''
    spot_rate = 1.10  # EUR/USD exchange rate
    strike_price = 1.05
    domestic_rate = 0.05  # USD interest rate
    foreign_rate = 0.03  # EUR interest rate
    volatility = 0.10  # 10% volatility
    time_to_maturity = 1.0  # 1 year to maturity
'''
    spot_rate = 7.12  # EUR/USD exchange rate
    strike_price = 7.75
    domestic_rate = 0.01929   # USD interest rate
    foreign_rate = 0.05032   # EUR interest rate
    volatility = 6.854/100  # 10% volatility
    time_to_maturity = 1.0  # 1 year to maturity
    # Calculate Gamma
    gamma = calculate_fx_option_gamma(
        spot_rate,
        strike_price,
        domestic_rate,
        foreign_rate,
        volatility,
        time_to_maturity
    )

    print(f"FX Option Gamma: {gamma:.6f}")


if __name__ == "__main__":
    main()