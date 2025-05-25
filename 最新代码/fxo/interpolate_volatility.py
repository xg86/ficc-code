def interpolate_volatility(delta, v_atm, rr_25, str_25):
    """
    Interpolates the implied volatility for a given delta using ATM volatility, 25-delta risk reversal, and 25-delta strangle.

    Parameters:
    delta (float): The target delta (e.g., 0.375 for 37.5-delta).
    v_atm (float): The ATM volatility.
    rr_25 (float): The 25-delta risk reversal (difference between 25-delta call and put volatilities).
    str_25 (float): The 25-delta strangle (average vol of 25-delta call and put minus ATM vol).

    Returns:
    float: Interpolated implied volatility for the target delta.
    """
    # Calculate x based on the target delta
    #if(delta < 0): #put
       # x = delta + 0.5
    #else:               #call
    #x = delta - 0.5

    x= delta
    # Apply the formula
    v_delta = v_atm - 2 * rr_25 * x + 16 * str_25 * x ** 2
    return v_delta

def calculate_strangle_delta_vol(vol_25_call, vol_25_put):
    """
    Calculate the strangle delta volatility by averaging the 25-delta call and put volatilities.

    Parameters:
    vol_25_call (float): Implied volatility of the 25-delta call.
    vol_25_put (float): Implied volatility of the 25-delta put.

    Returns:
    float: The strangle delta volatility.
    """
    return (vol_25_call + vol_25_put) / 2


def calculate_25_delta_strangle(v_atm, bf_25):
    """
    Calculate the 25-delta strangle from the ATM volatility, 25-delta risk reversal, and 25-delta butterfly.

    Parameters:
    v_atm (float): ATM volatility.
    rr_25 (float): 25-delta risk reversal.
    bf_25 (float): 25-delta butterfly.

    Returns:
    float: The 25-delta strangle.
    """
    str_25 = bf_25 + v_atm
    return str_25


# Example usage
v_atm = 0.10       # ATM volatility (10%)
rr_25 = 0.02       # 25-delta risk reversal (2%)
str_25 = 0.015     # 25-delta strangle (1.5%)

# Calculate the interpolated volatility for a 25-delta call and put
delta_call = 0.25
delta_put = -0.25

v_25_call = interpolate_volatility(delta_call, v_atm, rr_25, str_25)
v_25_put = interpolate_volatility(delta_put, v_atm, rr_25, str_25)
print(f"Interpolated volatility for 25-delta call: {v_25_call:.4f}")
print(f"Interpolated volatility for 25-delta put: {v_25_put:.4f}")

v_atm_1m = (4.71+5.31)/2/100  # ATM volatility (10%)
rr_25_1m = (-0.442+0.158)/2/100 # 25-delta risk reversal (2%)
bf_25_1m = (0.130+0.230)/2/100

delta_1m = -0.35  # put Target delta (37.5-delta)

vol_25_call = v_atm_1m+0.5*rr_25_1m+bf_25_1m
vol_25_put = v_atm_1m-0.5*rr_25_1m+bf_25_1m

print(f"vol_25_call: {vol_25_call:.4f}")
print(f"vol_25_put : {vol_25_put:.4f}")

#str_25_1m = calculate_strangle_delta_vol(vol_25_call, vol_25_put)  # 25-delta strangle (1.5%)
#print(f"str_25_1m with put and call : {str_25_1m:.4f}")
#v_37_5_1m = interpolate_volatility(delta_1m, v_atm_1m, vol_25_call-vol_25_put, str_25_1m)

print(f"PUT Interpolated volatility for {delta_1m * 100:.1f}-delta: {v_37_5_1m:.4f}")

str_25_1m = calculate_25_delta_strangle(v_atm_1m, bf_25_1m)
print(f"str_25_1m with v_atm_1m and bf_25_1m : {str_25_1m:.4f}")
v_37_5_1m = interpolate_volatility(delta_1m*-1, v_atm_1m, vol_25_call-vol_25_put, str_25_1m)

print(f"call Interpolated volatility for {delta_1m * 100:.1f}-delta: {v_37_5_1m:.4f}")

