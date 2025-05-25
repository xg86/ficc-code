import math
from scipy.stats import norm


def black_scholes_fx_option_price(
        spot_rate: float,
        strike_price: float,
        domestic_rate: float,
        foreign_rate: float,
        volatility: float,
        time_to_maturity: float,
        option_type: str = 'call'
) -> float:
    """
    Calculate FX Option Price using Black-Scholes model

    Parameters:
    - spot_rate: Current spot exchange rate
    - strike_price: Strike price of the option
    - domestic_rate: Domestic interest rate
    - foreign_rate: Foreign interest rate
    - volatility: Volatility of the exchange rate
    - time_to_maturity: Time to option maturity (in years)
    - option_type: 'call' or 'put'

    Returns:
    - Option price
    """
    # Calculate d1 and d2
    d1 = (
                 math.log(spot_rate / strike_price) +
                 (domestic_rate - foreign_rate + 0.5 * volatility ** 2) * time_to_maturity
         ) / (volatility * math.sqrt(time_to_maturity))

    d2 = d1 - volatility * math.sqrt(time_to_maturity)

    # Discount factors
    domestic_df = math.exp(-domestic_rate * time_to_maturity)
    foreign_df = math.exp(-foreign_rate * time_to_maturity)

    if option_type.lower() == 'call':
        return (
                spot_rate * foreign_df * norm.cdf(d1) -
                strike_price * domestic_df * norm.cdf(d2)
        )
    else:  # put option
        return (
                strike_price * domestic_df * norm.cdf(-d2) -
                spot_rate * foreign_df * norm.cdf(-d1)
        )


def calculate_gamma_finite_difference(
        spot_rate: float,
        strike_price: float,
        domestic_rate: float,
        foreign_rate: float,
        volatility: float,
        time_to_maturity: float,
        option_type: str = 'call',
        bump: float = 0.01  # 1% price bump
) -> float:
    """
    Calculate Gamma using Finite Difference Method

    Parameters:
    - bump: Percentage change in spot rate
    """
    # Calculate option price at current spot
    base_price = black_scholes_fx_option_price(
        spot_rate, strike_price, domestic_rate,
        foreign_rate, volatility, time_to_maturity, option_type
    )

    # Calculate option prices at slightly higher and lower spot rates
    up_spot = spot_rate * (1 + bump)
    down_spot = spot_rate * (1 - bump)

    up_price = black_scholes_fx_option_price(
        up_spot, strike_price, domestic_rate,
        foreign_rate, volatility, time_to_maturity, option_type
    )

    down_price = black_scholes_fx_option_price(
        down_spot, strike_price, domestic_rate,
        foreign_rate, volatility, time_to_maturity, option_type
    )

    # Calculate Gamma using finite difference formula
    gamma = (up_price - 2 * base_price + down_price) / (
            (spot_rate * bump) ** 2
    )

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
    domestic_rate = 0.01929  # USD interest rate
    foreign_rate = 0.05032  # EUR interest rate
    volatility = 6.854 / 100  # 10% volatility
    time_to_maturity = 1.0  # 1 year to maturity
    option_type = 'call'

    # Calculate Gamma using finite difference method
    gamma = calculate_gamma_finite_difference(
        spot_rate,
        strike_price,
        domestic_rate,
        foreign_rate,
        volatility,
        time_to_maturity,
        option_type
    )

    print(f"FX Option Gamma (Finite Difference): {gamma*1_000_000:.6f}")


if __name__ == "__main__":
    main()