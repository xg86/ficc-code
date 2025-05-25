import numpy as np

def american_option_binomial_tree_debug(S0, K, T, r, sigma, n, option_type='put'):
    dt = T / n
    u = np.exp(sigma * np.sqrt(dt))  # Up factor
    d = 1 / u                       # Down factor
    p = (np.exp(r * dt) - d) / (u - d)  # Risk-neutral probability

    # Initialize asset price tree
    S = np.zeros((n + 1, n + 1))
    for i in range(n + 1):
        for j in range(i + 1):
            S[j, i] = S0 * (u ** j) * (d ** (i - j))

    # Initialize option value tree
    V = np.zeros((n + 1, n + 1))
    for j in range(n + 1):
        if option_type == 'call':
            V[j, n] = max(S[j, n] - K, 0)
        elif option_type == 'put':
            V[j, n] = max(K - S[j, n], 0)

    # Backward induction to calculate option value
    exercise_boundary = [None] * n  # Initialize boundary list
    for i in range(n - 1, -1, -1):  # Iterate backward
        for j in range(i + 1):
            hold = np.exp(-r * dt) * (p * V[j + 1, i + 1] + (1 - p) * V[j, i + 1])
            if option_type == 'call':
                exercise = max(S[j, i] - K, 0)
            else:
                exercise = max(K - S[j, i], 0)
            V[j, i] = max(hold, exercise)

            # Capture exercise boundary (first point where exercise > hold)
            if exercise > hold and exercise_boundary[i] is None:
                exercise_boundary[i] = S[j, i]

    # Debugging: Detailed logs
    print("Debugging Exercise Boundary Detection")
    for i, boundary in enumerate(exercise_boundary):
        print(f"Step {i}, Boundary: {boundary}")

    return V[0, 0], exercise_boundary

# Parameters
'''
S0 = 1.2       # Initial FX rate (spot rate)
K = 1.1        # Strike price
T = 1          # Time to maturity in years
r = 0.05       # Risk-free rate
sigma = 0.2    # Volatility
n = 500        # Steps in the binomial tree (high resolution)
'''
# Parameters
S0 = 7.12       # Initial FX rate
K = 7.75        # Strike price
T = 1          # Time to maturity in years
r = 4.96882/100       # Risk-free rate
sigma = 6.9569/100   # Volatility
n = 100        # Steps in the binomial tree
price, boundary = american_option_binomial_tree_debug(S0, K, T, r, sigma, n, option_type='put')
print("\nOption Price:", price)
print("\nExercise Boundary:", boundary)
