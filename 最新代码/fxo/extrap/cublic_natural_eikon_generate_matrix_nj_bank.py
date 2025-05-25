import numpy as np
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d, CubicSpline
from numpy.polynomial.polynomial import Polynomial

class FXOptionCubicDeltaExtrapolator:
    def __init__(self, deltas, vols):
        """
        Initialize the extrapolator with FX option Delta RR and BF values

        :param deltas: List of delta values [10, 25, 50]
        :param rr_values: Corresponding Risk Reversal (RR) values
        :param bf_values: Corresponding Butterfly (BF) values
        """
        # Convert to numpy arrays for robust handling
        self.deltas_values = np.array(deltas)
        self.vol_values = np.array(vols)
        #self.coeffs_left = Polynomial.fit(self.deltas_values[:4], self.vol_values[:4], deg=2).convert().coef
        #self.coeffs_right = Polynomial.fit(self.deltas_values[-4:], self.vol_values[-4:], deg=2).convert().coef
        #self.cubic_interp = interp1d(self.deltas_values, self.vol_values, kind='cubic', fill_value="extrapolate")
        self.cubic_interp = CubicSpline(self.deltas_values, self.vol_values, bc_type='natural', extrapolate=True)

    # Define the cubic extrapolators
    #def cubic_extrapolate_left(self, xval):
        #return self.coeffs_left[0] + self.coeffs_left[1] * xval + self.coeffs_left[2] * xval ** 2

    #def cubic_extrapolate_right(self, xval):
        #return self.coeffs_right[0] + self.coeffs_right[1] * xval + self.coeffs_right[2] * xval ** 2

    # Combined interpolator and extrapolator
    def cubic_interp_extrap(self, xval):
        return self.cubic_interp(xval)


        '''
        if xval < self.deltas_values[0]:
            return self.cubic_extrapolate_left(xval)
        elif xval > self.deltas_values[-1]:
            return self.cubic_extrapolate_right(xval)
        else:
            return self.cubic_interp(xval)
        elif xval > 25 and xval < 50:
            return cubic_extrapolate_right(xval)
        elif xval > 50 and xval < 75:
            return cubic_extrapolate_left(xval)
        '''

def build_market_matrix(atm: float,vols:np.array, tenor:str, delta_df: DataFrame, index:int):
    # Example usage with different delta values
    # Inputs: 10D RR, 25D RR, 50D RR

    deltas = np.array([10, 25, 50, 75, 90])

    extrapolator = FXOptionCubicDeltaExtrapolator(deltas, vols)

    # Linear Extrapolation for 5 Delta RR and BF
    '''
    rr_5d_linear, bf_5d_linear = extrapolator.linear_extrapolation(15)
    print("Linear Extrapolation:")
    print("5 Delta RR:", rr_5d_linear)
    print("5 Delta BF:", bf_5d_linear)
    '''
    target_deltas = np.array([15, 20, 30, 35, 40, 45, 55, 60, 65, 70, 80, 85])

    # Weighted Interpolation for 5 Delta RR and BF

    for target_delta in target_deltas:
        vol_val = extrapolator.cubic_interp_extrap(target_delta)

        print(f"{tenor} {target_delta} Delta RR:  {vol_val:.6f}")
        #print(f"{tenor} {target_delta} Delta BF:  {bf_val:.6f}")
        if target_delta < 50:
            delta_df.at[index, str(target_delta)+'P'] = vol_val
        else:
            delta_df.at[index, str(100-target_delta) + 'C'] = vol_val
        #delta_df.at[index, str(target_delta)+'C'] = (atm + bf_val + rr_val/2)/100
        delta_df.at[index, 'ATM'] = atm




if __name__ == "__main__":
    market_vols = [
         {
           "Tenors": "ON",
           "10P": 4.375,
           "25P": 4.255,
           "ATM": 4,
           "25C": 4.205,
           "10C": 4.325
         },
         {
           "Tenors": "1W",
           "10P": 8.675,
           "25P": 8.555,
           "ATM": 8.3,
           "25C": 8.505,
           "10C": 8.625
         },
         {
           "Tenors": "2W",
           "10P": 8.45,
           "25P": 8.2925,
           "ATM": 8.1,
           "25C": 8.3675,
           "10C": 8.5
         },
         {
           "Tenors": "3W",
           "10P": 8.15,
           "25P": 7.9925,
           "ATM": 7.8,
           "25C": 8.0675,
           "10C": 8.25
         },
         {
           "Tenors": "1M",
           "10P": 7.385,
           "25P": 7.2475,
           "ATM": 7.05,
           "25C": 7.3225,
           "10C": 7.535
         },
         {
           "Tenors": "2M",
           "10P": 6.3,
           "25P": 6.145,
           "ATM": 5.925,
           "25C": 6.245,
           "10C": 6.5
         },
         {
           "Tenors": "3M",
           "10P": 6.15,
           "25P": 5.975,
           "ATM": 5.8,
           "25C": 6.175,
           "10C": 6.55
         },
         {
           "Tenors": "6M",
           "10P": 5.655,
           "25P": 5.48,
           "ATM": 5.375,
           "25C": 5.83,
           "10C": 6.255
         },
         {
           "Tenors": "9M",
           "10P": 5.48,
           "25P": 5.2775,
           "ATM": 5.2,
           "25C": 5.6775,
           "10C": 6.28
         },
         {
           "Tenors": "1Y",
           "10P": 5.325,
           "25P": 5.135,
           "ATM": 5.125,
           "25C": 5.685,
           "10C": 6.425
         },
         {
           "Tenors": "18M",
           "10P": 5.37,
           "25P": 5.2275,
           "ATM": 5.2,
           "25C": 5.7525,
           "10C": 6.57
         },
         {
           "Tenors": "2Y",
           "10P": 5.485,
           "25P": 5.325,
           "ATM": 5.3,
           "25C": 5.875,
           "10C": 6.685
         },
         {
           "Tenors": "3Y",
           "10P": 8.5,
           "25P": 9.5,
           "ATM": 6,
           "25C": 14.5,
           "10C": 21.5
         }
        ]

columns = ["Tenors", "1P", "5P", "10P", "15P", "20P", "25P", "30P", "35P", "40P", "45P","ATM",
                     "45C","40C", "35C", "30C", "25C", "20C", "15C", "10C", "5C", "1C"] # Create an empty DataFrame with the specified columns empty_df = pd.DataFrame(columns=columns)

matrix_df = pd.DataFrame(columns=columns)

matrix_df['Tenors'] = [
"ON",
"1W",
"2W",
"3W",
"1M",
"2M",
"3M",
"6M",
"9M",
"1Y",
"18M",
"2Y",
"3Y"]

for vol, index in zip(market_vols, enumerate(matrix_df['Tenors'])):
    vol_vals= []
    vol_vals.append(vol['10P'])
    vol_vals.append(vol['25P'])
    vol_vals.append(vol['ATM'])
    vol_vals.append(vol['25C'])
    vol_vals.append(vol['10C'])

    build_market_matrix(vol['ATM'], vol_vals, vol['Tenors'], matrix_df, index[0])
    print("$$$$$$$$$$$$$$$$$$$$$$$$")

print(matrix_df.to_string())
matrix_df.to_csv('cublic_natural_eikon_generate_matrix_pc.csv', index=False)