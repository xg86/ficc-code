import numpy as np
import matplotlib.pyplot as plt

def fx_forward_price(S0, r_d, r_f, T):
    """
    Calculate the forward price of an FX rate using interest rate parity.

    Parameters:
        S0 (float): Spot exchange rate (USD/CNY).
        r_d (float): Domestic risk-free rate (CNY rate).
        r_f (float): Foreign risk-free rate (USD rate).
        T (float): Time to maturity (in years).

    Returns:
        F (float): Forward exchange rate.
    """
    F = S0 * np.exp((r_d - r_f) * T)
    return F

def fx_option_price(F, S0, K, T, r_d, r_f, sigma, option_type, N=100, M=100):
    """
    Calculate the price of a European FX option using the Black-Scholes PDE model,
    with the forward price incorporated.

    Parameters:
        S0 (float): Spot exchange rate (USD/CNY).
        K (float): Strike price.
        T (float): Time to maturity (in years).
        r_d (float): Domestic risk-free rate (CNY rate).
        r_f (float): Foreign risk-free rate (USD rate).
        sigma (float): Volatility of the exchange rate.
        option_type (str): 'call' or 'put'.
        N (int): Number of time steps.
        M (int): Number of space steps.

    Returns:
        option_value (float): The option price at S0.
    """
    # Calculate forward price
    #F = fx_forward_price(S0, r_d, r_f, T)

    # Grid parameters
    S_max = 2 * F  # Maximum exchange rate for the grid (based on forward price)
    dt = T / N  # Time step size
    ds = S_max / M  # Exchange rate step size

    # Initialize grid
    V = np.zeros((M + 1, N + 1))  # Option value grid
    S = np.linspace(0, S_max, M + 1)  # Exchange rate grid

    # Terminal condition (payoff at maturity)
    if option_type == 'call':
        V[:, N] = np.maximum(S - K, 0)  # Call option payoff
    elif option_type == 'put':
        V[:, N] = np.maximum(K - S, 0)  # Put option payoff
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")

    # Boundary conditions
    if option_type == 'call':
        V[0, :] = 0  # At S = 0, call option value is 0
        V[M, :] = S_max - K * np.exp(-r_d * (T - np.linspace(0, T, N + 1)))  # At S -> infinity
    elif option_type == 'put':
        V[0, :] = K * np.exp(-r_d * (T - np.linspace(0, T, N + 1)))  # At S = 0, put option value is K * e^(-r_d * (T-t))
        V[M, :] = 0  # At S -> infinity, put option value is 0

    # Coefficients for the Crank-Nicolson scheme
    alpha = 0.25 * dt * (sigma**2 * (np.arange(M + 1)**2) - (r_d - r_f) * np.arange(M + 1))
    beta = -0.5 * dt * (sigma**2 * (np.arange(M + 1)**2) + r_d)
    gamma = 0.25 * dt * (sigma**2 * (np.arange(M + 1)**2) + (r_d - r_f) * np.arange(M + 1))

    # Tridiagonal matrix setup
    A = np.diag(1 - beta[1:M]) + np.diag(-alpha[2:M], k=-1) + np.diag(-gamma[1:M-1], k=1)
    B = np.diag(1 + beta[1:M]) + np.diag(alpha[2:M], k=-1) + np.diag(gamma[1:M-1], k=1)

    # Time-stepping loop
    for j in range(N - 1, -1, -1):
        # Right-hand side vector
        rhs = B @ V[1:M, j + 1]
        # Add boundary terms
        rhs[0] += alpha[1] * V[0, j]
        rhs[-1] += gamma[M - 1] * V[M, j]
        # Solve the system A * V_{j} = rhs
        V[1:M, j] = np.linalg.solve(A, rhs)

    # Interpolate to get the option value at S0
    from scipy.interpolate import interp1d
    option_value = interp1d(S, V[:, 0], kind='linear')(S0)

    return option_value

#1Y
'''
S0 = 7.12  # Spot exchange rate (USD/CNY)
K = 7.75 # Strike price
T = 1 # Time to maturity (1 year)
r_d = 1.92927/100 # Domestic risk-free rate (CNY rate, 3%)
#r_f = 4.96882/100  # Foreign risk-free rate (USD rate, 1%)
r_f = 5.005/100  # Foreign risk-free rate (USD rate, 1%) #BBG
sigma = 6.95692/100  # Volatility of the exchange rate (15%)
F = 6.9069
'''

#5D
'''
S0 = 7.12  # Spot exchange rate (USD/CNY)
K = 7.14 # Strike price
T = 5/365 # Time to maturity (1 year)
r_d = 1.52738/100 # Domestic risk-free rate (CNY rate, 3%)
r_f = 4.01554/100  # Foreign risk-free rate (USD rate, 1%)
sigma = 4.20902/100  # Volatility of the exchange rate (15%)
F = 7.118283
'''


#6D
S0 = 7.12  # Spot exchange rate (USD/CNY)
K = 7.07 # Strike price
T = 6/365 # Time to maturity (1 year)
r_d = 1.55614086534798/100 # Domestic risk-free rate (CNY rate, 3%)
r_f = 4.12568224828235/100  # Foreign risk-free rate (USD rate, 1%)
sigma = 8.12178056178724/100  # Volatility of the exchange rate (15%)
F = 7.11771428571429

'''
C:\anaconda3\envs\py39\python.exe C:/git/ficc-code/最新代码/fxo/deepSeek/bs-pde3.py
Forward Price of USD/CNY: 7.1177
European FX Call Option Value at S0 = 7.12: 595.1033
European FX Put Option Value at S0 = 7.12: 125.2913
'''



# Calculate forward price
#F = fx_forward_price(S0, r_d, r_f, T)

print(f"Forward Price of USD/CNY: {F:.4f}")

# Calculate call and put option prices
call_price = fx_option_price(F, S0, K, T, r_d, r_f, sigma, option_type='call')
put_price = fx_option_price(F, S0, K, T, r_d, r_f, sigma, option_type='put')

# Output the results
print(f"European FX Call Option Value at S0 = {S0}: {call_price*10_000:.4f}")
print(f"European FX Put Option Value at S0 = {S0}: {put_price*10_000:.4f}")