import numpy as np
import math
import matplotlib.pyplot as plt


class FXOptionExerciseBoundary:
    def __init__(self, spot_price, strike_price, volatility,
                 r_domestic, r_foreign, time_to_expiry, option_type):
        self.spot_price = spot_price
        self.strike_price = strike_price
        self.volatility = volatility
        self.r_domestic = r_domestic
        self.r_foreign = r_foreign
        self.time_to_expiry = time_to_expiry
        self.option_type = option_type

    def calculate_boundary(self, num_steps=100):
        dt = self.time_to_expiry / num_steps
        u = math.exp(self.volatility * math.sqrt(dt))
        d = 1 / u

        # Risk-neutral probability
        risk_neutral_prob = (math.exp((self.r_domestic - self.r_foreign) * dt) - d) / (u - d)

        # Initialize price and option trees
        price_tree = np.zeros((num_steps + 1, num_steps + 1))
        option_tree = np.zeros((num_steps + 1, num_steps + 1))
        exercise_boundary = np.zeros(num_steps + 1)

        # Build underlying price tree
        for i in range(num_steps + 1):
            for j in range(i + 1):
                price_tree[j, i] = self.spot_price * (u ** (i - j)) * (d ** j)

        # Terminal payoff
        for j in range(num_steps + 1):
            if self.option_type == 'call':
                option_tree[j, num_steps] = max(0, price_tree[j, num_steps] - self.strike_price)
            else:  # put
                option_tree[j, num_steps] = max(0, self.strike_price - price_tree[j, num_steps])

        # Backward induction with exercise boundary tracking
        for i in range(num_steps - 1, -1, -1):
            for j in range(i + 1):
                # Continuation value
                continuation = math.exp(-self.r_domestic * dt) * (
                        risk_neutral_prob * option_tree[j, i + 1] +
                        (1 - risk_neutral_prob) * option_tree[j + 1, i + 1]
                )

                # Intrinsic value
                if self.option_type == 'call':
                    intrinsic = max(0, price_tree[j, i] - self.strike_price)
                else:  # put
                    intrinsic = max(0, self.strike_price - price_tree[j, i])

                # Early exercise decision and boundary tracking
                option_tree[j, i] = max(intrinsic, continuation)

                # Track exercise boundary
                if intrinsic > continuation:
                    exercise_boundary[i] = price_tree[j, i]

        return option_tree[0, 0], exercise_boundary

    def plot_exercise_boundary(self, exercise_boundary):
        plt.figure(figsize=(10, 6))
        plt.plot(exercise_boundary[exercise_boundary > 0])
        plt.title(f'{self.option_type.upper()} Option Exercise Boundary')
        plt.xlabel('Time Steps')
        plt.ylabel('Exchange Rate')
        plt.show()


# Example usage
'''
spot_rate = 1.10  # EUR/USD exchange rate
strike = 1.05  # Strike price
vol = 0.10  # 10% volatility
r_dom = 0.05  # 5% domestic interest rate
r_foreign = 0.02  # 2% foreign interest rate
time_to_expiry = 1  # 1 year to expiry
'''
spot_rate = 7.12       # Initial FX rate
strike = 7      # Strike price
time_to_expiry = 1          # Time to maturity in years
r_dom = 1.92927/100       # domestic interest rate
r_foreign = 4.96882/100   # 2% foreign interest rate
vol = 5.1271/100   # Volatility
n = 100        # Steps in the binomial tree



# Put Option
put_option = FXOptionExerciseBoundary(
    spot_rate, strike, vol, r_dom, r_foreign,
    time_to_expiry, 'put'
)
put_price, put_boundary = put_option.calculate_boundary()
print(f"\nFX Put Option Price: {put_price}")
print("Put Option Exercise Boundary:")
print(put_boundary[put_boundary > 0])
put_option.plot_exercise_boundary(put_boundary)


strike = 7.75       # Strike price
vol = 6.9569/100   # Volatility

# Call Option
call_option = FXOptionExerciseBoundary(
    spot_rate, strike, vol, r_dom, r_foreign,
    time_to_expiry, 'call'
)
call_price, call_boundary = call_option.calculate_boundary()
print(f"FX Call Option Price: {call_price}")
print("Call Option Exercise Boundary:")
print(call_boundary[call_boundary > 0])
call_option.plot_exercise_boundary(call_boundary)
