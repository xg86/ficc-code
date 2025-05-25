import math


def calculate_pd_bond(bond_spread_bps, time_horizon_years, recovery_rate=0.4):
    """
    Calculate the probability of default (PD) using bond spreads.

    Args:
    - bond_spread_bps (float): Bond spread in basis points (bps).
    - time_horizon_years (float): Time horizon for the calculation (in years).
    - recovery_rate (float): Recovery rate (percentage of bond value recovered in default).

    Returns:
    - float: Probability of default over the specified time horizon.
    """
    # Convert bond spread from bps to decimal (e.g., 100 bps = 1%)
    bond_spread = bond_spread_bps / 10000

    # Calculate default probability using the exponential formula
    pd = 1 - math.exp(-bond_spread * time_horizon_years / (1 - recovery_rate))
    print(-bond_spread * time_horizon_years / (1 - recovery_rate))
    print(math.exp(-bond_spread * time_horizon_years / (1 - recovery_rate)))
    return pd


# Example usage:
bond_spread_bps = 40.1702  # 200 bps = 2%
time_horizon_years = 1.6219  # 3 years
recovery_rates = [0.2,0.25,0.3,0.35,0.4]  # 40% recovery rate

for recovery_rate in recovery_rates:
    pd_bond = calculate_pd_bond(bond_spread_bps, time_horizon_years, recovery_rate)
    print(f"Probability of Default over {time_horizon_years} years: {pd_bond:.4%}")
