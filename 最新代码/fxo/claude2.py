import numpy as np
import math
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
from scipy.optimize import brentq


class AdvancedFXOptionExerciseBoundary:
    def __init__(self, spot_price, strike_price, volatility,
                 r_domestic, r_foreign, time_to_expiry, option_type):
        self.spot_price = spot_price
        self.strike_price = strike_price
        self.volatility = volatility
        self.r_domestic = r_domestic
        self.r_foreign = r_foreign
        self.time_to_expiry = time_to_expiry
        self.option_type = option_type

    def _black_scholes_price(self, S, K, T, r_domestic, r_foreign, sigma, option_type):
        """Calculate Black-Scholes option price"""
        d1 = (np.log(S / K) + (r_domestic - r_foreign + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == 'call':
            return S * np.exp(-r_foreign * T) * norm_cdf(d1) - K * np.exp(-r_domestic * T) * norm_cdf(d2)
        else:  # put
            return K * np.exp(-r_domestic * T) * norm_cdf(-d2) - S * np.exp(-r_foreign * T) * norm_cdf(-d1)

    def _continuation_value(self, S, t, r_domestic, r_foreign, sigma, K, T, option_type):
        """Calculate continuation value"""
        return self._black_scholes_price(S, K, T - t, r_domestic, r_foreign, sigma, option_type)

    def _early_exercise_value(self, S, K, option_type):
        """Calculate early exercise intrinsic value"""
        if option_type == 'call':
            return max(S - K, 0)
        else:
            return max(K - S, 0)

    def calculate_exercise_boundary(self, num_points=50):
        """Calculate smooth exercise boundary using advanced method"""
        time_grid = np.linspace(0, self.time_to_expiry, num_points)
        exercise_boundary = np.zeros(num_points)

        for i, t in enumerate(time_grid):
            remaining_time = self.time_to_expiry - t

            # Define objective function for finding exercise boundary
            def objective(S):
                continuation = self._continuation_value(
                    S, t, self.r_domestic, self.r_foreign,
                    self.volatility, self.strike_price,
                    self.time_to_expiry, self.option_type
                )
                intrinsic = self._early_exercise_value(
                    S, self.strike_price, self.option_type
                )
                return intrinsic - continuation

            # Find the boundary using root-finding method
            try:
                if self.option_type == 'call':
                    # For call: boundary is above strike
                    lower = self.strike_price
                    upper = self.spot_price * 2  # Large upper bound
                else:
                    # For put: boundary is below strike
                    lower = self.spot_price * 0.5  # Low lower bound
                    upper = self.strike_price

                boundary = brentq(objective, lower, upper)
                exercise_boundary[i] = boundary
            except ValueError:
                # If no solution found, use last known boundary
                exercise_boundary[i] = exercise_boundary[i - 1] if i > 0 else self.spot_price

        return time_grid, exercise_boundary

    def plot_exercise_boundary(self, time_points, boundary):
        plt.figure(figsize=(12, 7))
        plt.plot(time_points, boundary, label='Exercise Boundary')
        plt.title(f'{self.option_type.upper()} Option Exercise Boundary')
        plt.xlabel('Time to Expiry')
        plt.ylabel('Exchange Rate')
        plt.axhline(y=self.strike_price, color='r', linestyle='--', label='Strike Price')
        plt.legend()
        plt.grid(True)
        plt.show()


# Cumulative standard normal distribution function
def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


# Example usage
scenarios = [
    {
    'spot_rate': 7.12,  # USD/CNY exchange rate
    'strike': 7.1,  # Strike price
    'vol': 5.5090/ 100,  # volatility
    'r_dom': 1.92927 / 100,  # domestic interest rate
    'r_foreign': 4.96882 / 100,  # foreign interest rate
    'time_to_expiry': 1  # 1 year to expiry
    },
    {
    'spot_rate': 7.12,  # USD/CNY exchange rate
    'strike': 7.3,  # Strike price
    'vol': 5.9375 / 100,  # volatility
    'r_dom': 1.92927 / 100,  # domestic interest rate
    'r_foreign': 4.96882 / 100,  # foreign interest rate
    'time_to_expiry': 1  # 1 year to expiry
    },
    {
    'spot_rate': 7.12,  # USD/CNY exchange rate
    'strike': 7.75,  # Strike price
    'vol': 6.9569 / 100,  # volatility
    'r_dom': 1.92927 / 100,  # domestic interest rate
    'r_foreign': 4.96882 / 100,  # foreign interest rate
    'time_to_expiry': 1  # 1 year to expiry
    }

]
for scenario in scenarios:
    for option_type in ['call']:
        print(f"\n--- {option_type.upper()} Option ---")
        option = AdvancedFXOptionExerciseBoundary(
            scenario['spot_rate'], scenario['strike'],
            scenario['vol'], scenario['r_dom'],
            scenario['r_foreign'], scenario['time_to_expiry'],
            option_type
        )

        time_points, exercise_boundary = option.calculate_exercise_boundary()

        print("Exercise Boundary Points:")
        for t, b in zip(time_points, exercise_boundary):
            print(f"Time: {t:.4f}, Boundary: {b:.4f}")

        option.plot_exercise_boundary(time_points, exercise_boundary)