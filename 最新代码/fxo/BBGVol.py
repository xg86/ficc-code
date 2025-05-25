import numpy as np
from scipy.stats import norm
from scipy.interpolate import CubicSpline
from scipy.optimize import root_scalar

#generate from BBG doc
class VolatilitySurfaceConstructor:
    def __init__(self, forward_rate, maturity):
        """
        Initialize volatility surface constructor

        :param forward_rate: Forward FX rate
        :param maturity: Time to maturity
        """
        self.F = forward_rate
        self.T = maturity

    def calculate_da(self, strike):
        """
        Calculate normalized distance metric

        :param strike: Option strike price
        :return: Normalized distance metric
        """
        sigma_ref = 1.5  # Reference volatility scaling
        return np.log(self.F / strike) / (sigma_ref * np.sqrt(self.T))

    def quadratic_volatility_form(self, strike, a, b, c):
        """
        Quadratic volatility functional form

        :param strike: Option strike price
        :param a, b, c: Quadratic function coefficients
        :return: Volatility estimate
        """
        da = self.calculate_da(strike)
        return a * norm.cdf(da) ** 2 + b * norm.cdf(da) + c

    def error_correction_function(self, market_vols, strikes, fitted_vols):
        """
        Construct error correction function using cubic spline

        :param market_vols: Market-observed volatilities
        :param strikes: Corresponding strike prices
        :param fitted_vols: Quadratic fitted volatilities
        :return: Cubic spline error correction function
        """
        residuals = market_vols - fitted_vols
        moneyness = np.log(strikes / self.F)

        # Cubic spline interpolation of residuals
        return CubicSpline(moneyness, residuals)

    def fit_volatility_smile(self, strikes, market_vols):
        """
        Fit volatility smile using quadratic functional form

        :param strikes: Array of strike prices
        :param market_vols: Corresponding market volatilities
        :return: Fitted volatility function
        """
        # Convert inputs to NumPy arrays to ensure proper calculations
        strikes = np.array(strikes)
        market_vols = np.array(market_vols)

        # Objective function for optimization
        def objective(params):
            a, b, c = params
            # Use list comprehension with NumPy array conversion
            fitted_vols = np.array([self.quadratic_volatility_form(k, a, b, c) for k in strikes])
            # Now we can perform element-wise subtraction
            return np.sum((fitted_vols - market_vols) ** 2)

        # Optimize coefficients
        from scipy.optimize import minimize
        initial_guess = [0.1, 0.1, 0.1]
        result = minimize(objective, initial_guess)
        a, b, c = result.x

        # Fitted quadratic volatilities
        fitted_vols = np.array([self.quadratic_volatility_form(k, a, b, c) for k in strikes])

        # Error correction function
        error_func = self.error_correction_function(market_vols, strikes, fitted_vols)

        def volatility_at_strike(strike):
            """
            Get volatility at a specific strike

            :param strike: Option strike price
            :return: Interpolated volatility
            """
            quadratic_vol = self.quadratic_volatility_form(strike, a, b, c)
            error_correction = error_func(np.log(strike / self.F))
            return quadratic_vol + error_correction

        return volatility_at_strike

    def convert_delta_to_strike(self, delta, option_type='call'):
        """
        Convert delta to strike price using root-finding

        :param delta: Option delta
        :param option_type: 'call' or 'put'
        :return: Corresponding strike price
        """

        def delta_difference(strike):
            # Black-Scholes delta calculation (simplified)
            d1 = (np.log(self.F / strike) + 0.5 * 0.2 ** 2 * self.T) / (0.2 * np.sqrt(self.T))

            if option_type == 'call':
                calculated_delta = norm.cdf(d1)
            else:
                calculated_delta = norm.cdf(d1) - 1

            return calculated_delta - delta

        # Find strike that gives the desired delta
        result = root_scalar(delta_difference, method='brentq', bracket=[-10, 10])
        return result.root


def main():
    # Example usage
    forward_rate = 1.10  # EUR/USD forward rate
    maturity = 1.0  # 1 year

    # Create volatility surface constructor
    vol_surface = VolatilitySurfaceConstructor(forward_rate, maturity)

    # Example market volatilities
    strikes = [1.05, 1.08, 1.10, 1.12, 1.15]
    market_vols = [0.15, 0.12, 0.10, 0.11, 0.13]

    # Fit volatility smile
    vol_func = vol_surface.fit_volatility_smile(strikes, market_vols)

    # Demonstrate volatility retrieval
    print("Volatility at different strikes:")
    for strike in strikes:
        print(f"Strike {strike}: {vol_func(strike):.4f}")

    # Convert delta to strike example
    delta_25_call_strike = vol_surface.convert_delta_to_strike(0.25, 'call')
    print(f"\nStrike for 25-delta call: {delta_25_call_strike:.4f}")

    # Get volatility at delta-equivalent strike
    vol_at_delta_strike = vol_func(delta_25_call_strike)
    print(f"Volatility at 25-delta strike: {vol_at_delta_strike:.4f}")


if __name__ == "__main__":
    main()