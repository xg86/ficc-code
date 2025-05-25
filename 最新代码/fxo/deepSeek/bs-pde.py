import numpy as np
import matplotlib.pyplot as plt

# Parameters for USD/CNY FX option
S0 = 7.12  # Spot exchange rate (USD/CNY)
K = 7.14 # Strike price
T = 6/365 # Time to maturity (1 year)
r_d = 1.52738/100 # Domestic risk-free rate (CNY rate, 3%)
r_f = 4.01554/100  # Foreign risk-free rate (USD rate, 1%)
sigma = 4.20902/100  # Volatility of the exchange rate (15%)

# Grid parameters
N = 100  # Number of time steps
M = 100  # Number of space steps
S_max = 2 * S0  # Maximum exchange rate for the grid
dt = T / N  # Time step size
ds = S_max / M  # Exchange rate step size

# Initialize grid
V = np.zeros((M + 1, N + 1))  # Option value grid
S = np.linspace(0, S_max, M + 1)  # Exchange rate grid

# Terminal condition (payoff at maturity)
V[:, N] = np.maximum(S - K, 0)  # Call option payoff

# Boundary conditions
V[0, :] = 0  # At S = 0, option value is 0
V[M, :] = S_max - K * np.exp(-r_d * (T - np.linspace(0, T, N + 1)))  # At S -> infinity

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

# Output the result
print(f"European FX Call Option Value at S0 = {S0}: {option_value*10000:.4f}")

# Plot the option value surface
plt.figure(figsize=(10, 6))
plt.plot(S, V[:, 0], label="Option Value at t=0")
plt.xlabel("Exchange Rate (USD/CNY)")
plt.ylabel("Option Value")
plt.title("European FX Call Option Value")
plt.legend()
plt.grid()
plt.show()