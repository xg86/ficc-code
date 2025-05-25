import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.optimize import brentq


class FlexibleFXOptionExerciseBoundary:
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

    def calculate_exercise_boundary(self, num_points=200, detailed_output=True):
        """
        Calculate exercise boundary with more points and optional detailed output

        Args:
        num_points (int): Number of points to calculate along the time axis
        detailed_output (bool): Whether to print detailed boundary information

        Returns:
        tuple: time points and corresponding exercise boundary values
        """
        time_grid = np.linspace(0, self.time_to_expiry, num_points)
        exercise_boundary = np.zeros(num_points)

        for i, t in enumerate(time_grid):
            remaining_time = self.time_to_expiry - t

            # Define objective function for finding exercise boundary
            def objective(S):
                # Continuation value using Black-Scholes
                continuation = self._black_scholes_price(
                    S, self.strike_price, remaining_time,
                    self.r_domestic, self.r_foreign,
                    self.volatility, self.option_type
                )

                # Intrinsic value
                if self.option_type == 'call':
                    intrinsic = max(S - self.strike_price, 0)
                else:  # put
                    intrinsic = max(self.strike_price - S, 0)

                return intrinsic - continuation

            # Find the boundary using root-finding method
            try:
                if self.option_type == 'call':
                    # For call: boundary is above strike
                    lower = self.strike_price
                    upper = max(self.spot_price * 2, self.strike_price * 2)
                else:
                    # For put: boundary is below strike
                    lower = max(self.spot_price * 0.5, self.strike_price * 0.5)
                    upper = self.strike_price

                boundary = brentq(objective, lower, upper)
                exercise_boundary[i] = boundary
            except ValueError:
                # Fallback if no solution found
                exercise_boundary[i] = exercise_boundary[i - 1] if i > 0 else self.spot_price

        # Detailed output option
        if detailed_output:
            print(f"{self.option_type.upper()} Option Exercise Boundary Details:")
            print(f"Total Points: {num_points}")
            print(f"Min Boundary: {exercise_boundary.min():.4f}")
            print(f"Max Boundary: {exercise_boundary.max():.4f}")
            print(f"Mean Boundary: {exercise_boundary.mean():.4f}")
            print(f"Median Boundary: {np.median(exercise_boundary):.4f}")

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
scenario_call = {
    'spot_rate': 7.12,  # USD/CNY exchange rate
    'strike': 7.3,  # Strike price
    'vol': 5.9375 / 100,  # volatility
    'r_dom': 1.92927 / 100,  # domestic interest rate
    'r_foreign': 4.96882 / 100,  # foreign interest rate
    'time_to_expiry': 1  # 1 year to expiry
}

for option_type in ['call']:
    print(f"\n--- {option_type.upper()} Option ---")
    option = FlexibleFXOptionExerciseBoundary(
        scenario_call['spot_rate'], scenario_call['strike'],
        scenario_call['vol'], scenario_call['r_dom'],
        scenario_call['r_foreign'], scenario_call['time_to_expiry'],
        option_type
    )

    time_points, exercise_boundary = option.calculate_exercise_boundary(
        num_points=365,  # Increased number of points
        detailed_output=True
    )

    option.plot_exercise_boundary(time_points, exercise_boundary)
    print("Exercise Boundary Points:")
    for t, b in zip(time_points, exercise_boundary):
        print(f"Time: {t:.4f}, Boundary: {b:.4f}")


scenario_put = {
    'spot_rate': 7.12,  # USD/CNY exchange rate
    'strike': 6.97,  # Strike price
    'vol': 5.2972/ 100,  # volatility
    'r_dom': 1.92927 / 100,  # domestic interest rate CNY
    'r_foreign': 1.96882 / 100,  # foreign interest rate USD
    'time_to_expiry': 218/365  # 1 year to expiry
}

for option_type in ['put']:
    print(f"\n--- {option_type.upper()} Option ---")
    option = FlexibleFXOptionExerciseBoundary(
        scenario_put['spot_rate'], scenario_put['strike'],
        scenario_put['vol'], scenario_put['r_dom'],
        scenario_put['r_foreign'], scenario_put['time_to_expiry'],
        option_type
    )

    time_points, exercise_boundary = option.calculate_exercise_boundary(
        num_points=218,  # Increased number of points
        detailed_output=True
    )

    option.plot_exercise_boundary(time_points, exercise_boundary)
    print("Exercise Boundary Points:")
    for t, b in zip(time_points, exercise_boundary):
        print(f"Time: {t:.4f}, Boundary: {b:.4f}")
