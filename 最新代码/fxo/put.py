import numpy as np
import matplotlib.pyplot as plt

def gen_stock_tree(S_0, sigma, T, n):
    dt = T / n
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    S = np.zeros((n + 1, n + 1))
    S[0, 0] = S_0
    for j in range(1, n + 1):
        S[:,j]= S[:,j-1]*u
        S[j,j]=S[j-1,j-1]*d
    return (u,d,S)


def american_put_boundary(S_0, K, rf, sigma, T, n):
    dt = T / n
    # obtain u, d, S_T from previous function
    u, d, S = gen_stock_tree(S_0, sigma, T, n)
    # risk-neutral probability calculation
    q = (np.exp(rf * dt) - d) / (u - d)
    # Grid (array) for storing option values
    P = np.zeros((n + 1, n + 1))
    # Initialize a list to store the stock prices that meet the condition
    temp_stock_prices = []

    boundary = np.append(np.full(n - 1, None), K)

    # Nested loop to iterate over nodes of the binomial tree
    for j in range(n - 1, -1, -1):
        for i in range(j + 1):
            # Calculate option value at node (i, j)
            P[i, j] = max(np.exp(-rf * dt) * (q * P[i, j + 1] + (1 - q) * P[i + 1, j + 1]), K - S[i, j])

            # Check if the option is exercised early at this node
            if P[i, j] == K - S[i, j]:
                # If so, store the corresponding stock price in the temporary array
                temp_stock_prices.append(S[i, j])

        # After iterating through all nodes in the current time step, check if temp_stock_prices is not empty
        if temp_stock_prices:
            # Find the maximum stock price from temp_stock_prices
            max_stock_price = max(temp_stock_prices)

            # Insert the maximum stock price into the boundary array at the matching index
            boundary[j] = max_stock_price

            # Clear temp_stock_prices for the next iteration
            temp_stock_prices = []

    print("\nExercise Boundary:", boundary)
    return (T, boundary)

#Input variables
'''
S_0= 100
K= 100
T=0.25
rf=0.1
sigma_values= [0.2,0.4]
n_values=[100,1000]
'''

S_0 = 7.12       # Initial FX rate
K = 6.86       # Strike price
T = 1          # Time to maturity in years
rf = 4.96882/100       # Risk-free rate
sigma_values = [5.1271/100]   # Volatility
n_values = [100]     # Steps in the binomial tree

# Generate exercise boundary for different values of sigma and n
exercise_boundary = {}
for sigma in sigma_values:
    for n in n_values:
        exercise_boundary[(sigma, n)] = american_put_boundary(S_0, K, rf, sigma, T, n)


plt.figure(figsize=(10, 6))
for sigma in sigma_values:
    for n in n_values:
        n1,prices=exercise_boundary[(sigma, n)]
        plt.plot(np.linspace(0, T, n), prices, label=f"σ={sigma}, n={n}")
plt.xlabel('Time (T)')
plt.ylabel('Exercise Boundary')
plt.title('Exercise Boundary for American Put Option')
plt.legend()
plt.grid(True)
plt.show()