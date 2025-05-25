import numpy as np
from scipy.stats import norm
from scipy.optimize import root_scalar


class FXOptionDeltaStrikeCalculator:
    def __init__(self, spot, domestic_rate, foreign_rate, volatility, time_to_maturity):
        """
        Initializes the calculator with market parameters.

        Parameters:
        - spot (float): The current spot price of the FX pair.
        - domestic_rate (float): The domestic interest rate.
        - foreign_rate (float): The foreign interest rate.
        - volatility (float): The implied volatility of the option.
        - time_to_maturity (float): Time to expiration in years.
        """
        self.spot = spot
        self.domestic_rate = domestic_rate
        self.foreign_rate = foreign_rate
        self.volatility = volatility
        self.time_to_maturity = time_to_maturity

    def delta_call(self, strike):
        """
        Calculates the delta of a call option given a strike price.

        Parameters:
        - strike (float): The strike price of the option.

        Returns:
        - float: The delta of the call option.
        """
        d1 = (np.log(self.spot / strike) + (
                    self.domestic_rate - self.foreign_rate + 0.5 * self.volatility ** 2) * self.time_to_maturity) / (
                         self.volatility * np.sqrt(self.time_to_maturity))
        delta_call = np.exp(-self.foreign_rate * self.time_to_maturity) * norm.cdf(d1)
        return delta_call

    def delta_put(self, strike):
        """
        Calculates the delta of a put option given a strike price.

        Parameters:
        - strike (float): The strike price of the option.

        Returns:
        - float: The delta of the put option.
        """
        #print(f"The strike price is: {strike:.4f}")

        d1 = (np.log(self.spot / strike) + (
                    self.domestic_rate - self.foreign_rate + 0.5 * self.volatility ** 2) * self.time_to_maturity) / (
                         self.volatility * np.sqrt(self.time_to_maturity))
        delta_put = np.exp(-self.foreign_rate * self.time_to_maturity) * (norm.cdf(d1) - 1)
        return delta_put

    def find_strike_for_delta(self, target_delta, option_type='call'):
        """
        Finds the strike price that corresponds to a specified delta.

        Parameters:
        - target_delta (float): The target delta value (e.g., 0.25 for a 25-delta call).
        - option_type (str): 'call' for call options, 'put' for put options.

        Returns:
        - float: The strike price corresponding to the specified delta.
        """
        if option_type == 'call':
            delta_function = lambda K: self.delta_call(K) - target_delta
        elif option_type == 'put':
            delta_function = lambda K: self.delta_put(K) - target_delta
        else:
            raise ValueError("Invalid option type. Use 'call' or 'put'.")

        # Define a reasonable range for the strike price
        result = root_scalar(delta_function, bracket=[self.spot * 0.5, self.spot * 1.5], method='bisect')

        if result.converged:
            return result.root
        else:
            raise ValueError("Could not find a strike for the target delta.")


# Example usage
def get_strike_for_delta(volatility: float, time_to_maturity:float, delta: float, opt_type:str):
    calculator = FXOptionDeltaStrikeCalculator(
        spot=7.12000,
        domestic_rate=0.0192927,
        foreign_rate=0.0503185,
        volatility=volatility,
        time_to_maturity=time_to_maturity
    )
    td = delta if opt_type == 'call' else delta * -1
    strike = calculator.find_strike_for_delta(td, option_type=opt_type)
    print(f"The strike price for a {td * 100:.0f}-delta {opt_type} is: {strike:.4f}")


if __name__ == "__main__":
    # Initialize the calculator with FX option parameters
    calculator = FXOptionDeltaStrikeCalculator(
        spot=7.12000,
        domestic_rate=0.0192927,
        foreign_rate=0.0503185,
        volatility=0.0889,
        #volatility=0.05325,
        time_to_maturity=1
    )

    # Calculate the strike price for a 25-delta call
    target_delta = -0.375 # - for put, + for call

    strike_for_target_delta = calculator.find_strike_for_delta(target_delta, option_type='put')
    print(f"The strike price for a {target_delta * 100:.0f}-delta call is: {strike_for_target_delta:.4f}")
    '''
    deltra_matrix_1y = np.array([
        #vol, time,delta, call/put, 1 or -1
        [0.05325, 1, 0.1, "put"],
        [0.05135, 1, 25/100, "put"],
        [0.05125, 1, 50/100, "call"],
        [0.05685, 1, 25/100, "call"],
        [0.06425, 1, 10/100, "call"]
    ])
    deltra_matrix_ON = np.array([
        # vol, time,delta, call/put, 1 or -1
        [0.043750, 1/365, 0.1, "put"],
        [0.04255, 1/365, 25 / 100, "put"],
        [0.04, 1/365, 50 / 100, "call"],
        [0.04205, 1/365, 25 / 100, "call"],
        [0.043250, 1/365, 10 / 100, "call"]
    ])

    deltra_matrix_1M = np.array([
        # vol, time,delta, call/put, 1 or -1
        [0.07385, 1 / 12, 0.1, "put"],
        [0.072475, 1 / 12, 25 / 100, "put"],
        [0.070500, 1 / 12, 50 / 100, "call"],
        [0.073225, 1 / 12, 25 / 100, "call"],
        [0.075350, 1 / 12, 10 / 100, "call"]
    ])
  
    deltra_matrix_2M = np.array([
        # vol, time,delta, call/put, 1 or -1
        [0.063000, 2 / 12, 0.1, "put"],
        [0.061450, 2 / 12, 25 / 100, "put"],
        [0.059250, 2 / 12, 50 / 100, "call"],
        [0.062450, 2 / 12, 25 / 100, "call"],
        [0.065000, 2 / 12, 10 / 100, "call"]
    ])
     deltra_matrix_5D = np.array([
        # vol, time,delta, call/put, 1 or -1
        [0.0435, 5 / 365, 0.1, "put"],
        [0.0423, 5 / 365, 25 / 100, "put"],
        [0.04, 5 / 365, 50 / 100, "call"],
        [0.042300, 5 / 365, 25 / 100, "call"],
        [0.043500, 5 / 365, 10 / 100, "call"]
    ])
      '''


    deltra_matrix_6D = np.array([
        # vol, time,delta, call/put, 1 or -1
        [0.0825, 5 / 365, 0.1, "put"],
        [0.0813, 5 / 365, 25 / 100, "put"],
        [0.079000, 5 / 365, 50 / 100, "call"],
        [0.081300, 5 / 365, 25 / 100, "call"],
        [0.0825, 5 / 365, 10 / 100, "call"]
    ])
    for i in range(len(deltra_matrix_6D)):
       get_strike_for_delta(float(deltra_matrix_6D[i][0]), float(deltra_matrix_6D[i][1]), float(deltra_matrix_6D[i][2]), deltra_matrix_6D[i][3])