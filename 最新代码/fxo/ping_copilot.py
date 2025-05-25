import numpy as np
from scipy.interpolate import interp1d

# Given data
deltas = np.array([0.10, 0.25])
rrs = np.array([1.225/100, 0.55/100])  # 10D and 25D RR values
bfs = np.array([0.7/100, 0.265/100])  # 10D and 25D BF values

# Quadratic extrapolation for RR
rr_interp = np.poly1d(np.polyfit(deltas, rrs, 2))
rr5 = rr_interp(0.05)

# Quadratic extrapolation for BF
bf_interp = np.poly1d(np.polyfit(deltas, bfs, 2))
bf5 = bf_interp(0.05)

print(f"5D RR: {rr5*100:.4f}, 5D BF: {bf5*100:.4f}")
