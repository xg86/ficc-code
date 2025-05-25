import numpy as np
import math
import random

def custom_round(x):
        return math.ceil(x)

def simulate_exposure(num_simulations, time_steps, initial_exposure, volatility):
    """
    Simulates future exposure paths using a geometric Brownian motion model.

    Args:
    - num_simulations (int): Number of Monte Carlo simulations.
    - time_steps (int): Number of time steps.
    - initial_exposure (float): Initial exposure at t=0.
    - volatility (float): Volatility of exposure.

    Returns:
    - np.array: Simulated exposure paths.
    """
    dt = 1  # Assume 1 year per time step
    time_years = int(custom_round(time_steps))+1
    exposures = np.zeros((num_simulations, time_years))

    for i in range(num_simulations):
        exposures[i, 0] = initial_exposure
        for t in range(1, time_years):
            shock = np.random.normal(0, volatility * np.sqrt(dt))
            exposures[i, t] = exposures[i, t - 1] * np.exp(shock)

    return exposures


def expected_exposure(simulated_exposures):
    """
    Computes the expected exposure (EE) at each time step.

    Args:
    - simulated_exposures (np.array): Simulated exposure paths.

    Returns:
    - np.array: Expected exposure at each time step.
    """
    return np.flip(np.mean(simulated_exposures, axis=0))


def probability_of_default(hazard_rate, time_steps, recovery_rate):
    """
    Computes probability of default (PD) at each time step using hazard rate.

    Args:
    - hazard_rate (float): Constant hazard rate.
    - time_steps (int): Number of time steps.

    Returns:
    - np.array: Probability of default at each time step.
    """
    time_years = int(custom_round(time_steps))
    pd = np.zeros(time_years+1)

    for t in range(1, time_years):
        print(f"time_years: ${t:,.2f}")
        #pd[t] = 1 - np.exp(-hazard_rate * (t - t + 1))  # Default probability increment
        #pd = 1 - math.exp(-bond_spread * time_horizon_years / (1 - recovery_rate))
        pd[t] = 1 - np.exp(-hazard_rate * t) # Default probability increment
    pd[t+1] = 1 - np.exp(-hazard_rate * time_steps)
    return pd


def calculate_cva(ee, pd, recovery_rate):
    """
    Computes CVA using expected exposure and probability of default.

    Args:
    - ee (np.array): Expected exposure at each time step.
    - pd (np.array): Probability of default at each time step.
    - recovery_rate (float): Recovery rate.

    Returns:
    - float: Credit Valuation Adjustment (CVA).
    """
    lgd = 1 - recovery_rate  # Loss given default
    #print(lgd)
    #print(ee)
    #print(pd)
    return np.sum(ee * pd * lgd)

def get_vol_exposure(random_numbers):
    cds_spreads = np.array(random_numbers)
    # Convert to decimal (bps → fraction)
    cds_spreads = cds_spreads / 10_000  # Example: 100 bps → 0.01 (1%)

    # Compute log returns
    log_returns = np.diff(np.log(cds_spreads))
    # Estimate annualized volatility (assuming monthly CDS data)
    volatility = np.std(log_returns) #* np.sqrt(12)
    print(f"Estimated Market-Implied Exposure Volatility: {volatility:.2%}")
    return volatility

# Parameters
def estimate_hazard_rate(spread: float, recovery_rate) -> float:
    """
    Estimate the hazard rate (default intensity) from bond spread.

    :param spread: Bond spread (as a decimal, e.g., 2% = 0.02)
    :param recovery_rate: Assumed recovery rate (default = 40%)
    :return: Hazard rate (lambda)
    """
    return spread / (1 - recovery_rate)
num_simulations = 10000  # Monte Carlo simulations
#time_steps = 1.6219  # Time horizon (left years)
time_steps = 2.0192  # Time horizon (left years)
initial_exposure = 100_000_000  # Initial exposure ($1M), need to add interested
#volatility = 35.92/100  # Volatility of exposure (20%)

random_numbers = [round(random.uniform(40, 50), 2) for _ in range(20)] # z-spread for past 20 days, eithor markets or from credit curve
print(random_numbers)

volatility = get_vol_exposure(random_numbers)  # Volatility of exposure (20%) 20 days history z-spread

#recovery_rate = 0.2  # 20% recovery rate static
zSpread= 46.0494/10_000  # current z-spread

# Simulate exposure paths
simulated_exposures = simulate_exposure(num_simulations, time_steps, initial_exposure, volatility)

# Compute Expected Exposure (EE)
ee = expected_exposure(simulated_exposures)

# Compute Probability of Default (PD)

# Compute CVA
recovery_rates = [0.2,0.25,0.3,0.35,0.4]  # 40% recovery rate
for recovery_rate in recovery_rates:
    print(f"recovery_rate: ${recovery_rate:,.2f}")
    # hazard_rate = 40.1702/10_000 # 2% annual hazard rate, current z-spread

    hazard_rate =estimate_hazard_rate(zSpread, recovery_rate)  # 2% annual hazard rate, current z-spread
    print(f"hazard_rate: ${hazard_rate:,.8f}")

    pd = probability_of_default(hazard_rate, time_steps, recovery_rate)
    print(f"probability_of_default")
    print(pd*100) # UI display as %
    print(f"Computed expected_exposure")

    for e in ee:
        print("{:.2f}".format(e))
    cva_value = calculate_cva(ee, pd, recovery_rate)
    print(f"Computed CVA: ${cva_value:,.2f}")
