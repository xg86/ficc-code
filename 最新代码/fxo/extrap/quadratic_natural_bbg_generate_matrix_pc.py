import numpy as np
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d, CubicSpline
from numpy.polynomial.polynomial import Polynomial

class FXOptionQuadraticDeltaExtrapolator:
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
        #self.quadratic_interp = CubicSpline(self.deltas_values, self.vol_values, bc_type='natural', extrapolate=True)
        self.quadratic_interp = interp1d(self.deltas_values, self.vol_values, kind='quadratic', fill_value="extrapolate", assume_sorted=True)

    # Define the cubic extrapolators
    #def cubic_extrapolate_left(self, xval):
        #return self.coeffs_left[0] + self.coeffs_left[1] * xval + self.coeffs_left[2] * xval ** 2

    #def cubic_extrapolate_right(self, xval):
        #return self.coeffs_right[0] + self.coeffs_right[1] * xval + self.coeffs_right[2] * xval ** 2

    # Combined interpolator and extrapolator
    def cubic_interp_extrap(self, xval):
        return self.quadratic_interp(xval)


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

    extrapolator = FXOptionQuadraticDeltaExtrapolator(deltas, vols)

    # Linear Extrapolation for 5 Delta RR and BF
    '''
    rr_5d_linear, bf_5d_linear = extrapolator.linear_extrapolation(15)
    print("Linear Extrapolation:")
    print("5 Delta RR:", rr_5d_linear)
    print("5 Delta BF:", bf_5d_linear)
    '''
    target_deltas = np.array([5, 15, 35, 65, 85, 95])

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
    ''' POC Nanjing bank
    market_rr =[
             {
               "Tenors": "ON",
               "10RR": -0.05,
               "25RR": -0.05,
               "ATM": 4
             },
             {
               "Tenors": "1W",
               "10RR": -0.05,
               "25RR": -0.05,
               "ATM": 8.3
             },
             {
               "Tenors": "2W",
               "10RR": 0.05,
               "25RR": 0.075,
               "ATM": 8.1
             },
             {
               "Tenors": "3W",
               "10RR": 0.1,
               "25RR": 0.075,
               "ATM": 7.8
             },
             {
               "Tenors": "1M",
               "10RR": 0.15,
               "25RR": 0.08,
               "ATM": 7.05
             },
             {
               "Tenors": "2M",
               "10RR": 0.2,
               "25RR": 0.1,
               "ATM": 5.925
             },
             {
               "Tenors": "3M",
               "10RR": 0.4,
               "25RR": 0.2,
               "ATM": 5.8
             },
             {
               "Tenors": "6M",
               "10RR": 0.6,
               "25RR": 0.35,
               "ATM": 5.375
             },
             {
               "Tenors": "9M",
               "10RR": 0.8,
               "25RR": 0.4,
               "ATM": 5.2
             },
             {
               "Tenors": "1Y",
               "10RR": 1.1,
               "25RR": 0.55,
               "ATM": 5.125
             },
             {
               "Tenors": "18M",
               "10RR": 1.2,
               "25RR": 0.525,
               "ATM": 5.2
             },
             {
               "Tenors": "2Y",
               "10RR": 1.2,
               "25RR": 0.55,
               "ATM": 5.3
             },
             {
               "Tenors": "3Y",
               "10RR": 1.2,
               "25RR": 0.6,
               "ATM": 5.35
             }
        ]

    market_bf = [
                 {
                   "Tenors": "ON",
                   "ATM": 4,
                   "25BF": 0.23,
                   "10BF": 0.35
                 },
                 {
                   "Tenors": "1W",
                   "ATM": 8.3,
                   "25BF": 0.23,
                   "10BF": 0.35
                 },
                 {
                   "Tenors": "2W",
                   "ATM": 8.1,
                   "25BF": 0.23,
                   "10BF": 0.375
                 },
                 {
                   "Tenors": "3W",
                   "ATM": 7.8,
                   "25BF": 0.23,
                   "10BF": 0.4
                 },
                 {
                   "Tenors": "1M",
                   "ATM": 7.05,
                   "25BF": 0.24,
                   "10BF": 0.41
                 },
                 {
                   "Tenors": "2M",
                   "ATM": 5.925,
                   "25BF": 0.27,
                   "10BF": 0.475
                 },
                 {
                   "Tenors": "3M",
                   "ATM": 5.8,
                   "25BF": 0.275,
                   "10BF": 0.55
                 },
                 {
                   "Tenors": "6M",
                   "ATM": 5.375,
                   "25BF": 0.28,
                   "10BF": 0.58
                 },
                 {
                   "Tenors": "9M",
                   "ATM": 5.2,
                   "25BF": 0.2775,
                   "10BF": 0.68
                 },
                 {
                   "Tenors": "1Y",
                   "ATM": 5.125,
                   "25BF": 0.285,
                   "10BF": 0.75
                 },
                 {
                   "Tenors": "18M",
                   "ATM": 5.2,
                   "25BF": 0.29,
                   "10BF": 0.77
                 },
                 {
                   "Tenors": "2Y",
                   "ATM": 5.3,
                   "25BF": 0.3,
                   "10BF": 0.785
                 },
                 {
                   "Tenors": "3Y",
                   "ATM": 5.35,
                   "25BF": 0.3,
                   "10BF": 0.8
                 }
                ]
'''
#BBG
market_vols =[
 {
   "Tenors": "1W",
   "10P": 5.427,
   "25P": 5.246,
   "ATM": 5.195,
   "25C": 5.619,
   "10C": 5.922
 },
 {
   "Tenors": "2W",
   "10P": 5.57,
   "25P": 5.388,
   "ATM": 5.293,
   "25C": 5.753,
   "10C": 6.105
 },
 {
   "Tenors": "3W",
   "10P": 5.338,
   "25P": 5.151,
   "ATM": 5.125,
   "25C": 5.534,
   "10C": 5.942
 },
 {
   "Tenors": "1M",
   "10P": 5.028,
   "25P": 4.803,
   "ATM": 4.815,
   "25C": 5.278,
   "10C": 5.533
 },
 {
   "Tenors": "2M",
   "10P": 4.88,
   "25P": 4.69,
   "ATM": 4.69,
   "25C": 5.14,
   "10C": 5.45
 },
 {
   "Tenors": "3M",
   "10P": 4.785,
   "25P": 4.661,
   "ATM": 4.658,
   "25C": 5.114,
   "10C": 5.38
 },
 {
   "Tenors": "4M",
   "10P": 4.847,
   "25P": 4.712,
   "ATM": 4.682,
   "25C": 5.117,
   "10C": 5.437
 },
 {
   "Tenors": "5M",
   "10P": 4.912,
   "25P": 4.748,
   "ATM": 4.689,
   "25C": 5.115,
   "10C": 5.563
 },
 {
   "Tenors": "6M",
   "10P": 4.911,
   "25P": 4.758,
   "ATM": 4.673,
   "25C": 5.113,
   "10C": 5.584
 },
 {
   "Tenors": "9M",
   "10P": 4.959,
   "25P": 4.814,
   "ATM": 4.722,
   "25C": 5.156,
   "10C": 5.686
 },
 {
   "Tenors": "1Y",
   "10P": 4.996,
   "25P": 4.871,
   "ATM": 4.77,
   "25C": 5.224,
   "10C": 5.784
 },
 {
   "Tenors": "18M",
   "10P": 4.915,
   "25P": 4.869,
   "ATM": 4.775,
   "25C": 5.226,
   "10C": 5.785
 },
 {
   "Tenors": "2Y",
   "10P": 4.905,
   "25P": 4.851,
   "ATM": 4.755,
   "25C": 5.214,
   "10C": 5.775
 },
 {
   "Tenors": "3Y",
   "10P": 4.799,
   "25P": 4.736,
   "ATM": 4.63,
   "25C": 5.124,
   "10C": 5.646
 }
]

columns = ["Tenors", "1P", "5P", "10P", "15P", "20P", "25P", "30P", "35P", "40P", "45P","ATM",
                     "45C","40C", "35C", "30C", "25C", "20C", "15C", "10C", "5C", "1C"] # Create an empty DataFrame with the specified columns empty_df = pd.DataFrame(columns=columns)

matrix_df = pd.DataFrame(columns=columns)

matrix_df['Tenors'] = [
#"ON",
"1W",
"2W",
"3W",
"1M",
"2M",
"3M",
"4M",
"5M",
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
matrix_df.to_csv('quadratic_natural_bbg_generate_matrix_pc.csv', index=False)