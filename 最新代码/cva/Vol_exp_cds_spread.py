import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import random

random_numbers = [round(random.uniform(40, 50), 2) for _ in range(20)]
print(random_numbers)
cds_spreads = np.array(random_numbers)
# Example: Hypothetical 5-year CDS spreads in basis points (bps)
#cds_spreads = np.array([
#    100, 105, 110, 98, 120, 130, 125, 140, 115, 118, 122, 135, 128, 138, 145, 150, 140, 160, 155, 148
#])  # CDS spreads in bps

# Convert to decimal (bps → fraction)
cds_spreads = cds_spreads / 10_000  # Example: 100 bps → 0.01 (1%)

# Compute log returns
log_returns = np.diff(np.log(cds_spreads))

# Estimate annualized volatility (assuming monthly CDS data)
volatility = np.std(log_returns) * np.sqrt(12)

print(f"Estimated Market-Implied Exposure Volatility: {volatility:.2%}")

# Plot CDS spreads over time
plt.figure(figsize=(10, 5))
plt.plot(cds_spreads * 10_000, marker='o', linestyle='-', color='b', label="CDS Spread (bps)")
plt.xlabel("Time (Months)")
plt.ylabel("CDS Spread (bps)")
plt.title("Historical CDS Spreads")
plt.legend()
plt.grid()
plt.show()

# Plot log returns
plt.figure(figsize=(10, 5))
plt.plot(log_returns, marker='o', linestyle='-', color='r', label="CDS Log Returns")
plt.xlabel("Time (Months)")
plt.ylabel("Log Return")
plt.title("CDS Spread Log Returns")
plt.axhline(0, color='black', linewidth=0.8, linestyle="--")
plt.legend()
plt.grid()
plt.show()
