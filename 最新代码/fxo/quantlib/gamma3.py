import numpy as np

def binomial_tree_american_gamma(S, K, T, r_d, r_f, sigma, option_type="call", N=100):
    """
    Calculate the Gamma of an American-style FX option using the binomial tree method.

    Parameters:
        S (float): Spot price of the underlying currency.
        K (float): Strike price of the option.
        T (float): Time to maturity in years.
        r_d (float): Domestic risk-free interest rate.
        r_f (float): Foreign risk-free interest rate.
        sigma (float): Volatility of the underlying currency pair.
        option_type (str): 'call' or 'put'.
        N (int): Number of steps in the binomial tree.

    Returns:
        float: Gamma of the FX option.
    """
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))  # Up factor
    d = 1 / u                        # Down factor
    p = (np.exp((r_d - r_f) * dt) - d) / (u - d)  # Risk-neutral probability

    # Initialize asset prices at maturity
    ST = np.array([S * (u**j) * (d**(N - j)) for j in range(N + 1)])

    # Initialize option values at maturity
    if option_type == "call":
        option_values = np.maximum(ST - K, 0)
    elif option_type == "put":
        option_values = np.maximum(K - ST, 0)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    # Save the second-to-last level option values and asset prices for Gamma calculation
    option_values_prev = None
    ST_prev = None

    # Work backwards through the tree
    for i in range(N - 1, -1, -1):
        ST_prev = ST  # Save the current asset prices
        option_values_prev = option_values  # Save the current option values

        ST = ST[:i + 1]  # Reduce the size of the asset prices array
        option_values = (p * option_values[1:] + (1 - p) * option_values[:-1]) * np.exp(-r_d * dt)

        # Check for early exercise
        if option_type == "call":
            option_values = np.maximum(option_values, ST - K)
        elif option_type == "put":
            option_values = np.maximum(option_values, K - ST)

        # Calculate Gamma at the second-to-last level
        if i == 1:
            mid_idx = len(ST_prev) // 2
            gamma = (option_values_prev[mid_idx + 1] - 2 * option_values_prev[mid_idx] + option_values_prev[mid_idx - 1]) / ((ST_prev[mid_idx + 1] - ST_prev[mid_idx])**2)
            return gamma

# Example parameters
'''
S = 1.2       # Spot price
K = 1.25      # Strike price
T = 0.5       # Time to maturity in years
r_d = 0.02    # Domestic risk-free rate
r_f = 0.01    # Foreign risk-free rate
sigma = 0.15  # Volatility (15%)
N = 200       # Number of steps in the binomial tree
'''
S = 7.12  # Spot price (USD/CNY)
K = 7.14 # Strike price (USD/CNY)
T = 1.0/365 # Time to maturity in years
r_d = 1.47/100   # Domestic risk-free rate (CNY, in decimal form)
r_f  = 4.383/100  # Foreign risk-free rate (must be USD, in decimal form)
sigma = 4.324/100 # Implied volatility (in decimal form)
N = 200       # Number of steps in the binomial tree
# Calculate Gamma
gamma_value = binomial_tree_american_gamma(S, K, T, r_d, r_f, sigma, option_type="call", N=N)
print(f"Gamma (American binomial): {gamma_value*10_000:.6f}")
