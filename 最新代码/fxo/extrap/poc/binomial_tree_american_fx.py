import numpy as np
from math import exp, log, sqrt
from scipy.stats import norm


def binomial_tree_american_fx(S, K, T, r_us, r_cn, ATM_vol, RR, BF, option_type="call", n_steps=100):
    """
    Binomial Tree model for American-style FX option pricing with volatility smile adjustments.

    S     = Spot price of USD/CNY
    K     = Strike price in USD
    T     = Time to maturity in years
    r_us  = Risk-free interest rate (USD)
    r_cn  = Risk-free interest rate (CNY)
    ATM_vol = ATM volatility (implied, in %)
    RR    = Risk reversal volatility at 25 delta (in %)
    BF    = Butterfly volatility at 25 delta (in %)
    option_type = "call" or "put"
    n_steps  = Number of steps in the binomial tree
    """

    # Ensure n_steps is a positive integer
    if n_steps <= 0:
        raise ValueError("Number of steps (n_steps) must be a positive integer.")

    # Convert volatilities from percentages to decimals
    ATM_vol = ATM_vol / 100
    RR = RR / 100
    BF = BF / 100

    # Calculate the forward price
    F = S * exp((r_us - r_cn) * T)

    # Delta calculation for smile/surface adjustment
    def implied_vol(K, S, ATM_vol, RR, BF, T):
        """ Adjust volatility based on strike using RR and BF (smile/skew). """
        delta = (K - S) / S
        if delta > 0:  # Call option (positive delta)
            vol = ATM_vol + RR * (delta - 0.25)
        else:  # Put option (negative delta)
            vol = ATM_vol - RR * (delta + 0.25)

        vol += BF * (delta ** 2)  # Butterfly adjustment
        return max(vol, ATM_vol)

    # Calculate volatility for each node in the tree
    def calculate_volatility(i, n):
        """ Calculate volatility for each node at step i (out of n). """
        print(f"Calculating volatility: i = {i}, n = {n}")  # Debugging print statement
        if n == 0:
            raise ValueError("Number of steps (n) cannot be zero in calculate_volatility.")
        step = i / n
        return implied_vol(K, S * exp((r_us - r_cn) * step), ATM_vol, RR, BF, T)

    # Calculate up and down factors and risk-neutral probabilities
    dt = T / n_steps
    up_factor = exp((r_us - r_cn) * dt)
    down_factor = 1 / up_factor
    risk_neutral_prob = (exp((r_us - r_cn) * dt) - down_factor) / (up_factor - down_factor)

    # Initialize the price matrix for the binomial tree
    option_tree = np.zeros((n_steps + 1, n_steps + 1))

    # Set up the final payoff at maturity
    for i in range(n_steps + 1):
        S_T = S * (up_factor ** (n_steps - i)) * (down_factor ** i)
        if option_type == "call":
            option_tree[i, n_steps] = max(S_T - K, 0)  # Call payoff
        else:
            option_tree[i, n_steps] = max(K - S_T, 0)  # Put payoff

    # Work backwards through the tree
    for j in range(n_steps - 1, -1, -1):
        for i in range(j + 1):
            S_node = S * (up_factor ** (j - i)) * (down_factor ** i)
            vol_node = calculate_volatility(i, j)  # This is where the error might occur
            option_tree[i, j] = exp(-r_us * dt) * (
                        risk_neutral_prob * option_tree[i, j + 1] + (1 - risk_neutral_prob) * option_tree[i + 1, j + 1])

            # Check for early exercise for American options
