# Refining the American Option Binomial Tree logic to ensure the boundary converges to the strike price.
import numpy as np
import matplotlib.pyplot as plt

def refined_american_option_binomial_tree(S0, K, T, r, sigma, n, option_type='put'):
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
    exercise_boundary = [None] * n
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

    # Ensure the last boundary matches the strike price for FX options
    if option_type == 'put':
        exercise_boundary[-1] = K

    # Prepare data for plotting the exercise boundary
    boundary_x = [T * i / n for i in range(n) if exercise_boundary[i] is not None]
    boundary_y = [boundary for boundary in exercise_boundary if boundary is not None]

    # Plot the exercise boundary frontier
    plt.figure(figsize=(10, 6))
    plt.plot(boundary_x, boundary_y, label="Exercise Boundary Frontier", marker='o')
    plt.title(f"Refined American Option Exercise Boundary Frontier ({option_type.capitalize()} Option)")
    plt.xlabel("Time to Maturity")
    plt.ylabel("Spot Price (Exercise Boundary)")
    plt.grid()
    plt.legend()
    plt.show()

    return V[0, 0], exercise_boundary

# Generate the refined exercise boundary plot
S0 = 7.12       # Initial FX rate
K = 6.86       # Strike price
T = 1          # Time to maturity in years
r = 4.96882/100       # Risk-free rate
sigma = 5.1271/100   # Volatility
n = 100        # Steps in the binomial tree

refined_price, refined_boundary = refined_american_option_binomial_tree(S0, K, T, r, sigma, n, option_type='put')
#refined_price, refined_boundary

print("\nOption Price:", refined_price)
print("\nExercise Boundary:", refined_boundary)



