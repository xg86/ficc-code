import numpy as np
import matplotlib.pyplot as plt
import QuantLib as ql

d1 = -0.8418
# Create an instance of the CumulativeNormalDistribution
cnd = ql.CumulativeNormalDistribution()

# Calculate the cumulative normal distribution value
cdn_val = cnd(d1)

# Explicitly convert cdn_val to float
cnd_value_float = float(cdn_val)

print(cnd_value_float)
#print(f"cdn_val in : {cdn_val:.4f}")