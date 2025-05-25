import math
from scipy.stats import norm

def barone_adesi_whaley_fx(S, K, T, r_d, r_f, sigma, option_type="call"):
    """
    Price an American-style FX option using the Barone-Adesi Whaley approximation.

    Parameters:
        S (float): Spot price of the FX rate.
        K (float): Strike price of the option.
        T (float): Time to maturity in years.
        r_d (float): Domestic risk-free rate.
        r_f (float): Foreign risk-free rate.
        sigma (float): Volatility of the FX rate.
        option_type (str): 'call' or 'put'.

    Returns:
        float: Approximate price of the American FX option.
    """
    b = r_d - r_f
    d1 = (math.log(S / K) + (b + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if option_type == "call":
        # European call option price
        euro_price = S * math.exp((b - r_d) * T) * norm.cdf(d1) - K * math.exp(-r_d * T) * norm.cdf(d2)
        if b >= 0:
            return euro_price  # No early exercise benefit
        phi = 1
    elif option_type == "put":
        # European put option price
        euro_price = K * math.exp(-r_d * T) * norm.cdf(-d2) - S * math.exp((b - r_d) * T) * norm.cdf(-d1)
        phi = -1
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    # BWA parameters
    beta = (0.5 - b / sigma**2) + phi * math.sqrt(((b / sigma**2 - 0.5)**2) + 2 * r_d / sigma**2)
    B_infinity = beta / (beta - 1) * K
    B0 = max(K, r_d * K / (r_d - b))

    h = -(b * T + 2 * sigma * math.sqrt(T)) * (B0 / (B_infinity - B0))
    X = B0 + (B_infinity - B0) * (1 - math.exp(h))

    if option_type == "call":
        if S >= X:
            return S - K
        else:
            return euro_price + (S - X) * (1 - math.exp(-r_d * T))
    elif option_type == "put":
        if S <= X:
            return K - S
        else:
            return euro_price + (X - S) * (1 - math.exp(-r_d * T))

def gamma_bwa_fx(S, K, T, r_d, r_f, sigma, delta_S, option_type="call"):
    """
    Calculate Gamma for an American-style FX option using the BWA method.

    Parameters:
        S (float): Spot price of the FX rate.
        K (float): Strike price of the option.
        T (float): Time to maturity in years.
        r_d (float): Domestic risk-free rate.
        r_f (float): Foreign risk-free rate.
        sigma (float): Volatility of the FX rate.
        option_type (str): 'call' or 'put'.
        notional (float): Notional value of the option.
        delta_S (float): Small change in the spot price for finite difference.

    Returns:
        float: Gamma of the FX option scaled by the notional.
    """
    price_up = barone_adesi_whaley_fx(S + delta_S, K, T, r_d, r_f, sigma, option_type)
    price_down = barone_adesi_whaley_fx(S - delta_S, K, T, r_d, r_f, sigma, option_type)
    price_base = barone_adesi_whaley_fx(S, K, T, r_d, r_f, sigma, option_type)

    gamma = (price_up - 2 * price_base + price_down) / (delta_S**2)
    return gamma

# Example parameters
'''
S = 1.2         # Spot price
K = 1.25        # Strike price
T = 0.5         # Time to maturity in years
r_d = 0.02      # Domestic risk-free rate
r_f = 0.01      # Foreign risk-free rate
sigma = 0.15    # Volatility (15%)
'''
S = 7.12  # Spot price (USD/CNY)
K = 7.14  # Strike price (USD/CNY)
T = 1/365/24*21  # Time to maturity in years
r_d = 1.47/100  # Domestic risk-free rate (CNY, in decimal form)
r_f  = 4.383/100   # Foreign risk-free rate (must be USD, in decimal form)
sigma = 4.324/100  # Implied volatility (in decimal form)
#notional = 1_000_000  # Notional amount
delta_S = 7.12-7.1194  # Small change in spot price

# Calculate Gamma
gamma_value = gamma_bwa_fx(S, K, T, r_d, r_f, sigma, delta_S, option_type="call")
print(f"Gamma (BWA, American FX Option, Scaled by Notional): {gamma_value:.6f}")
